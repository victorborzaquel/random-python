from pytube import YouTube
import constants  

link = input("Digite o link do vídeo do YouTube: ")
yt = YouTube(link)
print(f"\nVideo found: {yt}\n")

audio_stream = yt.streams.get_audio_only()

print(f"Baixando: {yt.title}")
audio_stream.download(output_path=constants.tmp_path, filename=f"{yt.title}.mp3")
print(f"Áudio baixado com sucesso em: {constants.tmp_path}")
