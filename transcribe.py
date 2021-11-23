import grpc
import json
import argparse

##TODO: automatically configure Speech APIs and sort out auth

def transcribe_streaming(stream_file):
    """Streams transcription of the given audio file."""
    import io
    from google.cloud import speech

    client = speech.SpeechClient()

    # [START speech_python_migration_streaming_request]
    with io.open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=11025,
        #audio_channel_count=2,
        model='video',
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    # [START speech_python_migration_streaming_response]
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )
    # [END speech_python_migration_streaming_request]

    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        
        for result in response.results:
            print("Finished: {}".format(result.is_final))
            print("Stability: {}".format(result.stability))
            alternatives = result.alternatives
            # The alternatives are ordered from most likely to least.
            for alternative in alternatives:
                print("Confidence: {}".format(alternative.confidence))
                print(u"Transcript: {}".format(alternative.transcript))
    # [END speech_python_migration_streaming_response]


# [END speech_transcribe_streaming]

def transcribe_offline(batch_file):
    import io
    from google.cloud import speech
    from types import SimpleNamespace

    with io.open(batch_file, "r") as myfile:
        uris=myfile.readlines()

    for uri in uris:
        gcs_uri=uri.strip()
        print(gcs_uri)
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(uri=gcs_uri)
        diarization = speech.SpeakerDiarizationConfig(enable_speaker_diarization=True,min_speaker_count=2)

    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        language_code="en-US",
        audio_channel_count=1,
        enable_separate_recognition_per_channel=True,
        enable_automatic_punctuation=True,
        diarization_config=diarization
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete on {}...".format(uri.split('/')[-1]))
    fn=uri.split('/')[-1][0:12]    
    output_file = "{}.txt".format(fn)
    f=open(output_file, "w")

    response = operation.result(timeout=90)
    result = response.results[-1]

    words_info = result.alternatives[0].words
    
    prevSpeaker=words_info[0].speaker_tag
    #f.write("speakerTag: {}".format(prevSpeaker))

    # Printing out the output:
    for word_info in words_info:
        if word_info.speaker_tag != prevSpeaker:
            f.write("\n>>> ")
        f.write("{} ".format(word_info.word.upper()))
        prevSpeaker=word_info.speaker_tag
        #f.write("prevSpeaker: {}".format(prevSpeaker))
        #f.write("speaker_tag: {}".format(word_info.speaker_tag))

    f.close()


# [END transcribe_offline]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("mode",help="Use 'live' to test the streaming API or 'offline' for the offline API.")
    parser.add_argument("file",help="In live mode, provide an audio file in WAV format encoded at 11025 Hz. In offline mode, provide a text file with a list of Google Storage URLs in the form gs://bucket/filename.")
    #group = parser.add_mutually_exclusive_group(required=True)
    #group.add_argument("-b","--batch", help="Text file with list of GCS URIs to be transcribed offline.", type=str)
    #group.add_argument("-f","--file", help="Audio file to be streamed and transcribed (output to terminal).", type=str)
    args = parser.parse_args()

if args.mode == "live": transcribe_streaming(args.file)
if args.mode == "offline": transcribe_offline(args.file)

