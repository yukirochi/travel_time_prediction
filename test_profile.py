import yaml
import os

profile_path = os.path.expanduser('~/.dbt/profiles.yml')
try:
    with open(profile_path) as f:
        profiles = yaml.safe_load(f)
    print("✓ YAML is valid")
    print("✓ Profiles loaded:")
    for profile_name in profiles:
        print(f"  - {profile_name}")
        if profile_name == 'travel_time_prediction':
            print(f"    target: {profiles[profile_name].get('target')}")
            print(f"    outputs: {list(profiles[profile_name].get('outputs', {}).keys())}")
except Exception as e:
    print(f"✗ Error: {e}")
