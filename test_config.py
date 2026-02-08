import yaml

with open('nanobot_config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

print("[OK] Configuration loaded successfully")
print("\nJules Config:")
jules = config['agents']['jules']
print(f"  Model: {jules['model']}")
print(f"  Prompt: {jules['system_prompt'][:80]}...")

print("\nAgent Mapping:")
mapping = config['channels']['discord']['agent_mapping']
for key, value in mapping.items():
    print(f"  {key}: {value}")
