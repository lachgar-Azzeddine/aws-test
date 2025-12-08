#!/usr/bin/env python3
"""
Test script to verify all Gravitee APIM fixes
"""
import requests
import json
import sys

def test_logging_configuration():
    """Test that logging configuration can be added to APIs"""
    print("\n" + "="*60)
    print("TEST 1: Logging Configuration")
    print("="*60)

    api_url = "http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis"
    resp = requests.get(api_url, auth=('admin', 'admin'))
    apis = resp.json()

    if not apis:
        print("❌ No APIs found")
        return False

    api = apis[0]
    api_id = api['id']

    # Get full API
    full_url = f"http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}?scope=full"
    full_resp = requests.get(full_url, auth=('admin', 'admin'))
    full_data = full_resp.json()

    if isinstance(full_data, list):
        full_data = full_data[0]

    # Add logging
    if 'proxy' not in full_data:
        full_data['proxy'] = {}

    full_data['proxy']['logging'] = {
        'mode': 'CLIENT_PROXY',
        'content': 'HEADERS_PAYLOADS',
        'scope': 'REQUEST_RESPONSE'
    }

    # Update
    update_url = f"http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}"
    update_resp = requests.put(update_url, json=full_data, auth=('admin', 'admin'))

    if update_resp.status_code in [200, 201]:
        # Verify
        verify_resp = requests.get(full_url, auth=('admin', 'admin'))
        verify_data = verify_resp.json()
        if isinstance(verify_data, list):
            verify_data = verify_data[0]

        if 'proxy' in verify_data and 'logging' in verify_data['proxy']:
            logging_config = verify_data['proxy']['logging']
            if logging_config.get('mode') == 'CLIENT_PROXY':
                print("✅ Logging configuration added successfully")
                print(f"   Mode: {logging_config['mode']}")
                print(f"   Content: {logging_config['content']}")
                print(f"   Scope: {logging_config['scope']}")
                return True
            else:
                print("❌ Logging mode incorrect")
                return False
        else:
            print("❌ Logging configuration not found after update")
            return False
    else:
        print(f"❌ API update failed: {update_resp.status_code}")
        return False

def test_lifecycle_state():
    """Test that lifecycle_state can be set to PUBLISHED"""
    print("\n" + "="*60)
    print("TEST 2: API Lifecycle State")
    print("="*60)

    api_url = "http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis"
    resp = requests.get(api_url, auth=('admin', 'admin'))
    apis = resp.json()

    if not apis:
        print("❌ No APIs found")
        return False

    api = apis[0]
    api_id = api['id']

    # Get full API
    full_url = f"http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}?scope=full"
    full_resp = requests.get(full_url, auth=('admin', 'admin'))
    full_data = full_resp.json()

    if isinstance(full_data, list):
        full_data = full_data[0]

    # Update lifecycle_state
    full_data['lifecycle_state'] = 'PUBLISHED'

    # Update
    update_url = f"http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}"
    update_resp = requests.put(update_url, json=full_data, auth=('admin', 'admin'))

    if update_resp.status_code in [200, 201]:
        # Verify
        verify = requests.get(api_url, auth=('admin', 'admin'))
        verify_data = verify.json()
        api_after = [a for a in verify_data if a['id'] == api_id][0]

        lifecycle = api_after.get('lifecycle_state')
        if lifecycle == 'PUBLISHED':
            print(f"✅ Lifecycle state set to PUBLISHED")
            return True
        else:
            print(f"❌ Lifecycle state is {lifecycle}, expected PUBLISHED")
            return False
    else:
        print(f"❌ Lifecycle update failed: {update_resp.status_code}")
        return False

def test_custom_api_key_setting():
    """Test that custom API key setting can be checked"""
    print("\n" + "="*60)
    print("TEST 3: Custom API Key Setting")
    print("="*60)

    settings_url = "http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/settings"
    resp = requests.get(settings_url, auth=('admin', 'admin'))

    if resp.status_code == 200:
        settings = resp.json()
        custom_api_key = settings.get('plan', {}).get('security', {}).get('customApiKey', {}).get('enabled')

        if custom_api_key is True:
            print("✅ Custom API key is enabled in platform settings")
            return True
        else:
            print("⚠️  Custom API key is NOT enabled in platform settings")
            print("   This must be enabled manually in the UI:")
            print("   1. Access http://localhost:8082")
            print("   2. Go to Organization Settings > Plans")
            print("   3. Check 'Allow custom API-key'")
            return False
    else:
        print(f"❌ Failed to get settings: {resp.status_code}")
        return False

def test_api_count():
    """Test that all APIs are present"""
    print("\n" + "="*60)
    print("TEST 4: API Count")
    print("="*60)

    api_url = "http://localhost:8080/management/organizations/DEFAULT/environments/DEFAULT/apis"
    resp = requests.get(api_url, auth=('admin', 'admin'))

    if resp.status_code == 200:
        apis = resp.json()
        count = len(apis)
        print(f"✅ Found {count} APIs")

        # Check states
        started = [a for a in apis if a.get('state') == 'STARTED']
        published = [a for a in apis if a.get('lifecycle_state') == 'PUBLISHED']

        print(f"   Started: {len(started)}")
        print(f"   Published: {len(published)}")

        if count >= 19:
            return True
        else:
            print(f"⚠️  Expected at least 19 APIs, found {count}")
            return False
    else:
        print(f"❌ Failed to get APIs: {resp.status_code}")
        return False

def main():
    print("\n" + "="*60)
    print("GRAVITEE APIM FIXES VERIFICATION")
    print("="*60)

    results = []
    results.append(("Logging Configuration", test_logging_configuration()))
    results.append(("Lifecycle State", test_lifecycle_state()))
    results.append(("Custom API Key Setting", test_custom_api_key_setting()))
    results.append(("API Count", test_api_count()))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED - See details above")
    print("="*60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
