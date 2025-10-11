def test_imports():
    """Tüm gerekli kütüphanelerin doğru import edildiğini test eder"""
    
    try:
        import pandas as pd
        import numpy as np
        import sklearn
        import lime
        import shap
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        print("✅ All core libraries imported successfully!")
        print(f"📊 Pandas version: {pd.__version__}")
        print(f"🔢 NumPy version: {np.__version__}")
        print(f"🤖 Scikit-learn version: {sklearn.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_directories():
    """Veri klasörlerinin varlığını test eder"""
    import os
    
    required_dirs = [
        "data", "data/raw", "data/processed", "data/samples",
        "src", "models", "reports"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")

if __name__ == "__main__":
    print("🧪 Testing Installation...")
    print("=" * 50)
    
    if test_imports():
        test_data_directories()
        print("\n🎉 Installation test completed!")
    else:
        print("\n❌ Installation has issues. Check requirements.txt")