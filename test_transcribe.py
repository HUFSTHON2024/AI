import openai

def test_transcribe():
        client = openai.OpenAI(api_key=api_key)
    
    try:
        with open("test.mp4", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko"  
            )
            
            print("변환된 텍스트:")
            print(transcript.text)
            return transcript.text
            
    except Exception as e:
        print("에러 발생:", str(e))
        return None

if __name__ == "__main__":
    test_transcribe() 