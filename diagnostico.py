import os
import sys

print("=" * 50)
print("DIAGNÓSTICO DO SISTEMA")
print("=" * 50)

print(f"\n📁 Pasta atual do Python: {os.getcwd()}")
print(f"📁 Caminho completo: {os.path.abspath('.')}")

print(f"\n📄 Arquivos na pasta atual:")
for file in os.listdir('.'):
    print(f"   - {file}")

print(f"\n🔍 Verificando chatbot.js:")
if os.path.exists("chatbot.js"):
    print("   ✅ chatbot.js ENCONTRADO!")
    print(f"   📏 Tamanho: {os.path.getsize('chatbot.js')} bytes")
else:
    print("   ❌ chatbot.js NÃO ENCONTRADO!")
    
print(f"\n📁 Arquivos .js na pasta:")
for file in os.listdir('.'):
    if file.endswith('.js'):
        print(f"   - {file}")

input("\nPressione ENTER para sair...")