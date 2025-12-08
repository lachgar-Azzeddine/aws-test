#!/bin/sh

# This script creates a read-only Kubernetes user on a pre-defined cluster context.
# The user CANNOT read secrets.

# --- Step 1: Define the Target Kubernetes Context ---
# Hardcode the context name here. All operations will be performed on this cluster.
TARGET_CONTEXT="RKE2-APPS"


# --- Validation ---
# Verify that the specified context exists before proceeding.
echo "Verifying that context '${TARGET_CONTEXT}' exists..."
if ! kubectl config get-contexts "${TARGET_CONTEXT}" >/dev/null 2>&1; then
  echo "❌ Error: The specified context '${TARGET_CONTEXT}' does not exist in your kubeconfig."
  echo "Please check the context name and your ~/.kube/config file."
  exit 1
fi
echo "✅ Context found. Proceeding with target: ${TARGET_CONTEXT}"
echo


# --- Configuration ---
# Use the target context name to create a descriptive filename
KUBECONFIG_FILE_NAME="${TARGET_CONTEXT}-kc-viewer.yaml"
KUBECONFIG_DIR="${HOME}/.kube"
VIEWER_CLUSTER_ROLE_NAME="k-view-no-secrets"
VIEWER_NAMESPACE="readonly"
VIEWER_NAME="k-viewer-no-secrets"


# --- Cleanup ---
# Clean up resources from the TARGET context to make the script re-runnable.
echo "Cleaning up previous resources from '${TARGET_CONTEXT}' if they exist..."
kubectl --context=${TARGET_CONTEXT} delete clusterrolebinding ${VIEWER_NAME} --ignore-not-found
kubectl --context=${TARGET_CONTEXT} delete clusterrole ${VIEWER_CLUSTER_ROLE_NAME} --ignore-not-found
kubectl --context=${TARGET_CONTEXT} delete namespace ${VIEWER_NAMESPACE} --ignore-not-found


# --- RBAC and User Creation ---

# 1. Create the ClusterRole on the target cluster
echo "Creating ClusterRole on '${TARGET_CONTEXT}'..."
cat <<EOF | kubectl --context=${TARGET_CONTEXT} apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ${VIEWER_CLUSTER_ROLE_NAME}
rules:
- apiGroups: [""]
  resources:
  - componentstatuses
  - configmaps
  - endpoints
  - events
  - limitranges
  - namespaces
  - nodes
  - persistentvolumeclaims
  - persistentvolumes
  - pods
  - podtemplates
  - replicationcontrollers
  - resourcequotas
  - serviceaccounts
  - services
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps", "batch", "extensions", "networking.k8s.io", "rbac.authorization.k8s.io"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
EOF

# 2. Create the namespace and ServiceAccount on the target cluster
echo "Creating Namespace and ServiceAccount..."
kubectl --context=${TARGET_CONTEXT} create ns ${VIEWER_NAMESPACE}
kubectl --context=${TARGET_CONTEXT} create serviceaccount -n ${VIEWER_NAMESPACE} ${VIEWER_NAME}

# 3. Bind the role to the ServiceAccount on the target cluster
echo "Creating ClusterRoleBinding..."
kubectl --context=${TARGET_CONTEXT} create clusterrolebinding ${VIEWER_NAME} --clusterrole=${VIEWER_CLUSTER_ROLE_NAME} --serviceaccount=${VIEWER_NAMESPACE}:${VIEWER_NAME}

# 4. Create the token secret for the ServiceAccount
echo "Creating token secret..."
kubectl --context=${TARGET_CONTEXT} apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: ${VIEWER_NAME}-token
  namespace: ${VIEWER_NAMESPACE}
  annotations:
    kubernetes.io/service-account.name: "${VIEWER_NAME}"
type: kubernetes.io/service-account-token
EOF

echo "Waiting for token to be populated..."
sleep 5

# --- Kubeconfig Generation ---

# 5. Retrieve token and cluster info from the TARGET context
echo "Retrieving credentials and cluster info..."
TOKEN=$(kubectl --context=${TARGET_CONTEXT} -n ${VIEWER_NAMESPACE} get secret ${VIEWER_NAME}-token -o jsonpath='{.data.token}' | base64 --decode)
CA_CERT=$(kubectl --context=${TARGET_CONTEXT} -n ${VIEWER_NAMESPACE} get secret ${VIEWER_NAME}-token -o jsonpath='{.data.ca\.crt}' | base64 --decode)
TARGET_CLUSTER_NAME=$(kubectl config view -o jsonpath="{.contexts[?(@.name=='${TARGET_CONTEXT}')].context.cluster}")
KUBE_API=$(kubectl config view -o jsonpath="{.clusters[?(@.name=='${TARGET_CLUSTER_NAME}')].cluster.server}")

# 6. Assemble the Kubeconfig file
KUBECONFIG_FILE_PATH="${KUBECONFIG_DIR}/${KUBECONFIG_FILE_NAME}"
echo "Creating kubeconfig file at: ${KUBECONFIG_FILE_PATH}"

CA_CERT_FILE=$(mktemp)
echo "${CA_CERT}" > "${CA_CERT_FILE}"

KUBECONFIG=${KUBECONFIG_FILE_PATH} kubectl config set-cluster "${TARGET_CLUSTER_NAME}" --server="${KUBE_API}" --certificate-authority="${CA_CERT_FILE}" --embed-certs=true
KUBECONFIG=${KUBECONFIG_FILE_PATH} kubectl config set-credentials "${VIEWER_NAME}" --token="${TOKEN}"
KUBECONFIG=${KUBECONFIG_FILE_PATH} kubectl config set-context "${TARGET_CONTEXT}" --cluster="${TARGET_CLUSTER_NAME}" --user="${VIEWER_NAME}"
KUBECONFIG=${KUBECONFIG_FILE_PATH} kubectl config use-context "${TARGET_CONTEXT}"

rm -f "${CA_CERT_FILE}"

