import sys
sys.path.insert(0, "/home/rob_kaz/python/external_libraries/python-helpers")

"""
print_directory_tree(
    ".",
    max_depth=4,
    exclude_dirs={"__pycache__"},
    shallow_dirs={".git"},
    exclude_dir_patterns=["tests*", "*.egg-info"],
    exclude_file_extensions={".pyc", ".log", ".tmp"}
)
"""

# Linux version
try:
    from python_helpers.file_utils import print_directory_tree
    from python_helpers.string_utils import camel_to_snake
    print("✓ Import successful!")
    
    # Test the functions
    print("\n--- Testing print_directory_tree ---")
    #print_directory_tree(".", max_depth=3)
    print_directory_tree(
        ".",
        max_depth=5,
        exclude_dirs={"__pycache__"},
        shallow_dirs={
            ".git", 
            "cache",
            },
        exclude_dir_patterns=[
            "*.egg-info",
            "*.pytest_cache"],
        exclude_file_extensions={
            ".pyc", 
            ".log", 
            ".tmp", 
            ".Identifier",
            ".cpg",
            ".dbf",
            ".prj",
            ".sbn",
            ".sbx",
            ".shp",
            ".shp.xml",
            ".shx"
        }
)
    
    # print("\n--- Testing camel_to_snake ---")
    # test_string = "CamelCaseString"
    # result = camel_to_snake(test_string)
    # print(f"'{test_string}' -> '{result}'")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Function call failed: {e}")


# Windows version
# try:
    
  
#     from helpers.file_utils import print_directory_tree
#     from helpers.string_utils import camel_to_snake
#     print("✓ Import successful!")
    
#     # Test the functions
#     print("\n--- Testing print_directory_tree ---")
#     print_directory_tree(".", max_depth=3)
    
#     print("\n--- Testing camel_to_snake ---")
#     test_string = "CamelCaseString"
#     result = camel_to_snake(test_string)
#     print(f"'{test_string}' -> '{result}'")
    
# except ImportError as e:
#     print(f"❌ Import failed: {e}")
# except Exception as e:
#     print(f"❌ Function call failed: {e}")