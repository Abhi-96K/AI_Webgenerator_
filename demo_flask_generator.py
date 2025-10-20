#!/usr/bin/env python3
"""
Demo script showing the new Flask fullstack project generation capabilities
"""
import os
import tempfile
import zipfile
from pathlib import Path
from generator.flask_templates import generate_flask_project


def demo_flask_generation():
    """Demonstrate Flask project generation"""
    
    print("🚀 AI Website Generator - Flask Project Demo")
    print("=" * 50)
    
    # Test different types of applications
    test_prompts = [
        "Create a task management app for small teams with project organization",
        "Build an e-commerce store for selling handmade crafts", 
        "Make a personal blog platform with comment system",
        "Create a simple inventory management system for a small business"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        print("-" * 60)
        
        try:
            # Generate Flask project
            files = generate_flask_project(prompt)
            
            print(f"✅ Generated {len(files)} files")
            
            # Show project structure
            print("\n📁 Project Structure:")
            for filepath in sorted(files.keys()):
                if "/" in filepath:
                    folder = filepath.split("/")[0]
                    filename = filepath.split("/")[-1]
                    print(f"  📂 {folder}/")
                    print(f"    📄 {filename}")
                else:
                    print(f"  📄 {filepath}")
            
            # Create a demo output
            output_dir = Path(f"demo_output_{i}")
            output_dir.mkdir(exist_ok=True)
            
            # Save files to demo directory
            for filepath, content in files.items():
                file_path = output_dir / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
            
            print(f"💾 Files saved to: {output_dir.absolute()}")
            
            # Show some key file previews
            print("\n📋 Key Files Preview:")
            
            # Show README snippet
            if 'README.md' in files:
                readme_lines = files['README.md'].split('\n')[:10]
                print("\n  📖 README.md (first 10 lines):")
                for line in readme_lines:
                    print(f"    {line}")
            
            # Show requirements
            if 'requirements.txt' in files:
                print(f"\n  📦 requirements.txt:")
                for line in files['requirements.txt'].strip().split('\n'):
                    print(f"    {line}")
            
            # Show app.py snippet  
            if 'app.py' in files:
                app_lines = files['app.py'].split('\n')[:15]
                print(f"\n  🐍 app.py (first 15 lines):")
                for line in app_lines:
                    print(f"    {line}")
                    
        except Exception as e:
            print(f"❌ Error generating project: {e}")
            
        print("\n" + "="*60)


def create_sample_zip():
    """Create a sample zip file to show what users will get"""
    print("\n🗜️  Creating sample downloadable zip file...")
    
    # Generate a sample project
    files = generate_flask_project("Create a modern task management application with user authentication and project collaboration")
    
    # Create zip file
    zip_path = "sample_flask_app.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath, content in files.items():
            zipf.writestr(filepath, content)
    
    zip_size = os.path.getsize(zip_path) / 1024  # Size in KB
    print(f"✅ Created {zip_path} ({zip_size:.1f} KB)")
    print(f"📋 Contains {len(files)} files ready for development")
    
    return zip_path


if __name__ == "__main__":
    try:
        demo_flask_generation()
        
        # Create a sample zip
        sample_zip = create_sample_zip()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📌 Summary of improvements:")
        print("  • Now generates complete Flask applications instead of basic HTML")
        print("  • Includes user authentication & database models")
        print("  • Provides REST API endpoints")
        print("  • Features modern Bootstrap UI")
        print("  • Includes proper project structure & documentation")
        print("  • Ready for development with requirements.txt")
        print("  • Supports different application types (e-commerce, blog, tasks, etc.)")
        
        print(f"\n💡 Users will now get professional fullstack applications!")
        print(f"📥 Sample download: {sample_zip}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()