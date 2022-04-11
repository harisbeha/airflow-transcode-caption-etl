






for result in response.results:
    alternative = result.alternative[0]







    print(u"Waiting for operation to complete...")
    response = operation.result()
    transcript = []
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))
        transcript.append(alternative.transcript)
        for word in alternative.words:
            print(u"Confidence: {}".format(word.confidence, word.speaker_tag))



Elementlist
{"version", "overall_confidence", "end_time", "language", "keywords", "start_time", "segments"

Per segment 
    List of sequence dicts

SequenceModel:
    {"start_time", "speaker_change", "confidence", "confidence_score", "tokens"}

TokenModel 
List of Token dicts 

Per Token
{"start_time", "interpolated", "value", "end_time", "type", "display_as"}





---

Create accounts configured to Standard with either Standard,High fidelities (or the translation setting)
    - ES_Translate account
    - FR_Translate account
    - RU_Translate account
    - Chinese_Translate account
    - StandardAccount
    - StandardFastAccount

Cloud function trigger 
    - Trigger Airflow processing on Cirrus order (similar to now)

    - Use MainDjangoOperator to create the job w/ media_url + custom callback URL
    - Create simple, internal endpoint to run start_job with the passed in job_id + lock down 

Cloud function return trigger (original callback URL)
    - On return, hit callback URL to indicate that the job is complete
    - Pull elementlist from the completed job_id provided using MainDjangoOperator
    - Convert to whatever format was in the original order
    - Use CirrusDjangoOperator to format and save OutputProduct

Needs:
Cirrus needs key-file signing to create downloadable URLs 

Fallbacks 
- Interval to check that jobs HAVE started



    for word in alternative.words:
        print(u"Word: {}".format(word.word))
        print(
            u"Start time: {} seconds {} nanos".format(
                word.start_time.seconds, word.start_time.nanos
            )
        )
        print(
            u"End time: {} seconds {} nanos".format(
                word.end_time.seconds, word.end_time.nanos
            )
        )


# {'job_id': 
# elementlist_version
# iwp_name

# job_id,
#                      'job_name': job_name,
#                      'elementlist_version': core_elementlist.get_newest_element_list_version(
#                          job_id,
#                          iwp_name=named_version
#                          ),
#                      'iwp_name': clean_job_name(job_info['job_owner'], named_version) if named_version else ''
#                      }