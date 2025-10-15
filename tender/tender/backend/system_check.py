# system_check.py - Verify core systems
import importlib

def check_import(module_name, class_name=None):
    try:
        module = importlib.import_module(module_name)
        if class_name:
            getattr(module, class_name)
        print(f"✅ {module_name}" + (f".{class_name}" if class_name else ""))
        return True
    except Exception as e:
        print(f"❌ {module_name}" + (f".{class_name}" if class_name else "") + f" - {e}")
        return False

print("🔍 Checking System Components...")

components = [
    ("database", "SessionLocal"),
    ("auth", "create_access_token"),
    ("ai_services", "AIService"),
    ("document_processor", "DocumentProcessor"),
    ("readiness_scorer", "ReadinessScorer"),
    ("schemas", "UserResponse"),
    ("main", "app")
]

results = []
for module, class_name in components:
    result = check_import(module, class_name)
    results.append(result)

success_count = sum(results)
print(f"📊 Results: {success_count}/{len(results)} components OK")

if success_count == len(results):
    print("🎉 All systems ready!")
else:
    print("❌ Some components need fixing.")