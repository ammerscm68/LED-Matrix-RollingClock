import vlc
import time

# VLC Instanz und MediaPlayer anlegen
instance = vlc.Instance()
player = instance.media_player_new()
player.audio_set_volume(200) # Lautstärke

# Media setzen
media = instance.media_new("/home/lmc/python/sound1.mp3")
player.set_media(media)

# Equalizer erstellen
equalizer = vlc.AudioEqualizer()

# Mehrere Frequenzbänder anpassen (Beispiel)
equalizer.set_amp_at_index(0, 10)  # 60 Hz  +5 dB - Min/Max: -20 /+20
equalizer.set_amp_at_index(1, 10)  # 170 Hz +3 dB - Min/Max: -20 /+20
equalizer.set_amp_at_index(2, -10) # 310 Hz -2 dB - Min/Max: -20 /+20
equalizer.set_amp_at_index(3, -10) # 600 Hz -2 dB - Min/Max: -20 /+20
equalizer.set_amp_at_index(4, -10) # 1 kHz -2 dB  - Min/Max: -20 /+20
equalizer.set_amp_at_index(5, -10) # 3 kHz -2 dB  - Min/Max: -20 /+20
equalizer.set_amp_at_index(6, -10) # 6 kHz -2 dB  - Min/Max: -20 /+20
equalizer.set_amp_at_index(7, -10) # 12 kHz -2 dB - Min/Max: -20 /+20
equalizer.set_amp_at_index(8, -10) # 14 kHz -2 dB - Min/Max: -20 /+20
equalizer.set_amp_at_index(9, 20) # 16 kHz -2 dB  - Min/Max: -20 /+20

# Equalizer auf den Player anwenden
player.set_equalizer(equalizer)

# Wiedergabe starten
player.play()

time.sleep(10) # kurz warten

# Wiedergabe stoppen
player.stop()