"""
Simple test script to verify the implementation.
Run this to check if all the new modules can be imported correctly.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all new modules can be imported."""
    print("Testing imports...")

    try:
        from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
        print("✓ app.core.security imported successfully")

        from app.models.user import User
        from app.models.comment import Comment
        print("✓ app.models.user and app.models.comment imported successfully")

        from app.schemas.user import UserCreate, UserRead, UserUpdate, Token, LoginRequest
        from app.schemas.comment import CommentCreate, CommentRead
        from app.schemas.pagination import PaginatedResponse
        print("✓ All new schemas imported successfully")

        from app.api.v1.endpoints import auth, comments, upload
        print("✓ All new endpoints imported successfully")

        print("\n✓ All imports successful!")
        return True

    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_security_functions():
    """Test basic security functions."""
    print("\nTesting security functions...")

    try:
        from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

        # Test password hashing
        password = "test123"
        hashed = hash_password(password)
        print(f"✓ Password hashed: {hashed[:20]}...")

        # Test password verification
        is_valid = verify_password(password, hashed)
        assert is_valid == True
        print("✓ Password verification works")

        # Test token creation
        token = create_access_token(data={"sub": "123"})
        print(f"✓ Token created: {token[:20]}...")

        # Test token decoding
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        print("✓ Token decoding works")

        print("\n✓ Security functions work correctly!")
        return True

    except Exception as e:
        print(f"\n✗ Security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Backend Implementation Test")
    print("=" * 50)

    success = True
    success &= test_imports()
    success &= test_security_functions()

    print("\n" + "=" * 50)
    if success:
        print("All tests passed! ✓")
    else:
        print("Some tests failed. ✗")
    print("=" * 50)

    sys.exit(0 if success else 1)
