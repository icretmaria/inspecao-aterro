[app]

# Título do app (aparece no celular)
title = Inspeção de Aterro

# Nome do pacote (sem espaços, tudo minúsculo)
package.name = inspecaoaterro

# Domínio do pacote (pode deixar assim)
package.domain = org.obra

# Arquivo principal do seu app
source.main = main.py

# Versão
version = 1.0

# ============================================================
# DEPENDÊNCIAS — tudo que seu app usa
# ============================================================
# fpdf2==2.7.9  → versão que NÃO usa o módulo 'cgi' (removido no Python 3.13)
# kivymd==1.2.0 → estável com kivy 2.3.0
# ezdxf==1.3.4  → versão testada no Android
requirements = python3,kivy==2.3.0,kivymd==1.2.0,fpdf2==2.7.9,ezdxf==1.3.4,plyer,android,pillow

# Orientação da tela
orientation = portrait

# Permissões Android necessárias
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Versão mínima do Android (Android 8.0+)
android.minapi = 26

# SDK alvo
android.sdk = 33

# NDK (não mexa nisso)
android.ndk = 25b

# Arquitetura (arm64-v8a funciona na maioria dos celulares modernos)
android.archs = arm64-v8a

# Features Android
android.features = android.hardware.camera, android.hardware.location.gps

# Aceitar automaticamente licenças do Android SDK
android.accept_sdk_license = True

[buildozer]

# Nível de log: 2 mostra mais detalhes de erro (útil para debug)
log_level = 2

warn_on_root = 1
