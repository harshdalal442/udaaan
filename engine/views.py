import calendar
import csv
import logging
import random
from datetime import date, timedelta
from datetime import datetime as dt
import editdistance
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
import pandas as pd
import math
import requests
import locale
from .serializers import *
from .utils import *

logger = logging.getLogger('my_logger')
def config_logger():
    try:
        log_file_name = 'EasyChatLog.log'
        logging_level = logging.INFO
        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file_name, when='midnight', backupCount=2000)
        handler.setFormatter(formatter)
        logger = logging.getLogger('my_logger')
        logger.addHandler(handler)
        logger.setLevel(logging_level)
        logger.propagate = False
    except Exception as e:
        logger.error("Error config_logger %s", str(e))


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

def do_pre_processing(message, channel, language):
    try:
        logger.info("Entered do_pre_processing")
        message = message.lower()
        message = remove_nonalphanumeric(message)
        message = remove_stopwords(message)
        #message = autocorrect(message, channel, language)
        message = preprocess_question(message)
        logger.info("After Preprocessing: %s", message)
        return message
    except Exception as e:
        logger.error("Error do_pre_processing Error %s", str(e))

def is_data_present(tree, user_id):
    print("IS Data Present")
    print("QuestionEntityType: ",tree.question_entity_type.name)
    data = Data.objects.filter(entity_name=tree.question_entity_type.name,
                               user__user_id=user_id)

    if data.count() > 0:
        return (True, data)
    else:
        return (False, "")

def provide_mapper_count(tree):
    return tree.mapper.all().count()

def get_next_tree_typable(tree):
    return tree.mapper.all()[0].next_tree

def returnNextTree(tree, user_id, pipe_temp, stage):
    try:
        logger.info("Entered returnNextTree")
        if tree.question_entity_type.entity_group.is_loop:
            print("InsideLoop")
            if stage == "pre":
                return (tree, pipe_temp)
            else:
                data_p = Data.objects.get(entity_name=tree.question_entity_type.name,
                                          user__user_id=user_id)
                cnt = data_p.cnt
                cnt = cnt - 1
                if cnt == 0:
                    data_p = Data.objects.filter(entity_name=tree.question_entity_type.name,
                                                 user__user_id=user_id)
                else:
                    data_p = Data.objects.filter(entity_name=tree.question_entity_type.name + str(cnt),
                                                 user__user_id=user_id)

                if data_p.count() > 0:
                    count = provide_mapper_count(tree)
                    if count == 1:
                        pipe_temp += data_p[0].entity_value + "|"
                        return returnNextTree(get_next_tree_typable(tree), user_id, pipe_temp, "pre")
                    else:
                        mappers = tree.mapper.all()
                        for mapper in mappers:
                            for data in data_p:
                                choice = data.entity_value
                                if (choice == mapper.entity.entity_name):
                                    pipe_temp += mapper.entity.entity_name + "|"
                                    if tree.question_entity_type.entity_group.is_primary:
                                        user = Profile.objects.get(user_id=user_id)
                                        user.current_entity = mapper.entity
                                        user.save()
                                    return returnNextTree(mapper.next_tree, user_id, pipe_temp, "pre")
                else:
                    return (tree, pipe_temp)
        else:
            print("Not loop")
            data_present = is_data_present(tree, user_id)
            print("data present", data_present)
            print(data_present)
            if data_present[0]:
                count = provide_mapper_count(tree)
                print(count)
                if count == 1:
                    pipe_temp += data_present[1][0].entity_value+"|"
                    print(pipe_temp)
                    return returnNextTree(get_next_tree_typable(tree), user_id, pipe_temp, "pre")
                else:
                    mappers = tree.mapper.all()
                    for mapper in mappers:
                        for data in data_present[1]:
                            choice = data.entity_value
                            if (choice == mapper.entity.entity_name):
                                pipe_temp += mapper.entity.entity_name+"|"
                                if tree.question_entity_type.entity_group.is_primary:
                                    user = Profile.objects.get(user_id=user_id)
                                    user.current_entity = mapper.entity
                                    user.save()
                                return returnNextTree(mapper.next_tree, user_id, pipe_temp, "pre")
                return (tree, pipe_temp)
            else:
                return (tree, pipe_temp)
    except Exception as e:
        logger.error("Error returnNextTree %s", str(e))
        return (tree, pipe_temp)

def create_data_flow(tree, user_id, channel, pipe_temp):
    try:
        logger.info("Entered create_data_flow")
        json = {}

        if tree.question_entity_type.entity_group.is_typable:
            json["is_typable"] = "true"
        if tree.question_entity_type.entity_group.is_clickable:
            json["is_clickable"] = "true"
        if tree.question_entity_type.entity_group.is_date:
            json["is_date"] = True
        if tree.question_entity_type.entity_group.is_dropdown:
            json["is_dropdown"] = True
        if tree.question_entity_type.entity_group.is_file:
            json["is_file"] = True
        if tree.current_stage is not None:
            json["current_stage"] = tree.current_stage
        if tree.question_entity_type.intent_on_click is not None:
            json["redirect_intent"] = tree.question_entity_type.intent_on_click
        if tree.question_entity_type.entity_to_delete is not None:
            json["redirect_delete_entities"] = tree.question_entity_type.entity_to_delete.split(",")
        json["response"] = parse_sentence(tree.question_entity_type.question.sentence, tree.question_entity_type.question.file, user_id)
        #if Profile.objects.get(user_id=user_id).re_question:
        #    if tree.question_entity_type.re_question.sentence is not None:
        #        json["response"] = parse_sentence(tree.question_entity_type.re_question.sentence, tree.question_entity_type.question.file, user_id)
        json["choices"] = create_choice_list(tree.question_entity_type.entity_group)
        json["is_answer"] = "false"
        json["pipe"] = pipe_temp

        return json
    except Exception as e:
        logger.error("Error create_data_flow() %s", str(e))

def get_answer(tree, channel):
    for choice in tree.answer.group_of_sentences.all():
        if choice.channel.name == channel:
            return choice.sentence

def get_file(tree, channel):
    for choice in tree.answer.group_of_sentences.all():
        if choice.channel.name == channel:
            file = "999abc999"
            if choice.file is not None:
                file = choice.file
    return file

def save_analytics(user):
    try:
        AnalyticCount(intent=user.current_intent,
                      entity=user.current_entity).save()
    except Exception as e:
        logger.error("Error in save_analytics %s", str(e))

def create_upvote_downvote_links(user):
    upvote_link = "/queryfeedback/" + user.current_query + "/" + user.user_id + "/like"
    downvote_link = "/queryfeedback/" + user.current_query + "/" + user.user_id + "/dislike"

    return (upvote_link, downvote_link)

def get_recommendations(user):
    return recommendations(user.current_intent, user.current_entity)

def reset_user(user_id):
    try:
        user = Profile.objects.get(user_id=user_id)
        user.tree = None
        user.current_intent = None
        user.current_entity = None
        user.re_question = False
        user.stage = "pre"
        user.save()
    except Profile.DoesNotExist:
        logger.error("No matching profile found")

def clear_data_from_model(user_id):
    try:
        data = Data.objects.filter(user__user_id=user_id)
        for value in data:
            obj = QuestionsEntityGroup.objects.filter(name=value.entity_name)
            if obj.count() > 0:
                if not obj[0].entity_group.is_persistent:
                    Data.objects.filter(user__user_id=user_id,
                                        entity_name=value.entity_name).delete()
    except Data.DoesNotExist:
        logger.error("No matching data found")

def create_data_answer(tree, channel, user_id):
    try:
        logger.info("Entered create_data_answer")
        json = {}

        user = Profile.objects.get(user_id=user_id)
        save_analytics(user)
        json["is_typable"] = "true"
        print("Json is: ", json)
        json["response"] = parse_sentence(get_answer(tree, channel),get_file(tree,channel),user_id)
        print("Json is: ", json)
        (upvote_link, downvote_link) = create_upvote_downvote_links(user)
        json["upvote_link"] = upvote_link
        json["downvote_link"] = downvote_link
        json["is_answer"] = "true"
        print("Json is: ", json)
        json["recommended_queries"] = get_recommendations(user)
        clear_data_from_model(user_id)
        reset_user(user_id)
        return json
    except Profile.DoesNotExist:
        print("A")
        logger.error("No matching profile found")
    except Exception as e:
        print("Error create_data_answer() %s", str(e))
        logger.error("Error create_data_answer() %s", str(e))

def create_data_stages(tree, user_id, channel, pipe_temp):
    try:
        logger.info("Entered create_data_stages")

        if tree.question_entity_type is not None:
            json = create_data_flow(tree, user_id, channel, pipe_temp)
        else:
            json = create_data_answer(tree, channel, user_id)
        return json
    except Exception as e:
        logger.error("function: error_data_stages Error from create_data %s", str(e))

def validate_data_and_save_from_response(message, tree, user_id):
    try:
        if tree.question_entity_type.entity_group.is_typable:
            logger.info("Entered validate_data_and_save_from_response")
            entity_type = tree.question_entity_type.entity_group
            dataValidator = DataValidators.objects.filter(entity_type=entity_type)               ##################### Changed
            if len(dataValidator) == 0:
                dataValidator = DataValidators.objects.get(pk=2)
            else:
                dataValidator = dataValidator.get()
            print(dataValidator)
            d = {}
            exec (str(dataValidator.function), d)
            user_t = Profile.objects.get(user_id=user_id)
            if d['f'](message) is not None:
                logger.info("Value Is: %s", d['f'](message))
                print("Saving message", d['f'](message))

                redirect_intent = None
                if tree.question_entity_type.intent_on_click is not None:
                    redirect_intent = tree.question_entity_type.intent_on_click
                redirect_entities_delete = None
                if tree.question_entity_type.entity_to_delete is not None:
                    redirect_entities_delete = tree.question_entity_type.entity_to_delete

                try:
                    a = Data.objects.get(entity_name=tree.question_entity_type.name,
                                            user=user_t)
                    cntt = a.cnt
                    a.cnt = a.cnt + 1
                    a.save()

                    Data(entity_name=tree.question_entity_type.name+str(cntt),
                         entity_value=d['f'](message),
                         current_stage=tree.current_stage,
                         redirect_intent=redirect_intent,
                         redirect_entities_delete=redirect_entities_delete,
                         user=user_t).save()
                except:
                    Data(entity_name=tree.question_entity_type.name,
                         entity_value=d['f'](message),
                         current_stage=tree.current_stage,
                         redirect_intent=redirect_intent,
                         redirect_entities_delete=redirect_entities_delete,
                         user=user_t).save()
                return True
            else:
                user_t.re_question = True
                user_t.save()
                return False
    except DataValidators.DoesNotExist:
        logger.error("No matching extracter found")
    except Exception as e:
        logger.error("Error saveValueFromMessage %s", str(e))

def validate_choice_and_save_from_response(tree, entities, user_id):
    try:
        logger.info("Entered validate_choice_and_save_from_response")
        if tree.question_entity_type.entity_group.is_clickable:
            if entities is not None:
                entity_type = tree.question_entity_type.entity_group
                logger.info("Inside SaveEntity")
                for entity in entities:
                    entity_value = entity.entity_name
                    logger.info("Entity Type: %s", entity_type.name)
                    logger.info("Choice Value %s", entity_value)

                    redirect_intent = None
                    if tree.question_entity_type.intent_on_click is not None:
                        redirect_intent = tree.question_entity_type.intent_on_click
                    redirect_entities_delete = None
                    if tree.question_entity_type.entity_to_delete is not None:
                        redirect_entities_delete = tree.question_entity_type.entity_to_delete

                    try:
                        a = Data.objects.get(entity_name=tree.question_entity_type.name,
                                             user=Profile.objects.get(user_id=user_id))
                        cntt = a.cnt
                        a.cnt = a.cnt + 1
                        a.save()

                        Data(entity_name=tree.question_entity_type.name + str(cntt),
                             entity_value=entity_value,
                             current_stage=tree.current_stage,
                             redirect_intent=redirect_intent,
                             redirect_entities_delete=redirect_entities_delete,
                             user=Profile.objects.get(user_id=user_id)).save()
                    except:
                        Data(entity_name=tree.question_entity_type.name,
                             entity_value=entity_value,
                             current_stage=tree.current_stage,
                             redirect_intent=redirect_intent,
                             redirect_entities_delete=redirect_entities_delete,
                             user=Profile.objects.get(user_id=user_id)).save()
    except Exception as e:
        logger.error("Error Entered validate_choice_and_save_from_response %s", str(e))


def process_any_tree_with_stages_new(tree, entities, user_id, flag, channel, message, what, pipe_temp):
    try:
        logger.info("Entered process_any_tree_with_stages_new")
        current_user = Profile.objects.get(user_id=user_id)
        current_stage = current_user.stage
        if current_stage == "pre":
            print("Up")
            print(tree)
            (tree, pipe_temp) = returnNextTree(tree, user_id, pipe_temp, "pre")
            print(tree)
            print("Up")
            user = Profile.objects.get(user_id=user_id)
            user.tree = tree
            user.stage = "post"
            user.save()
            return create_data_stages(tree, user_id, channel, pipe_temp)
        else:
            to_delete = ""
            if tree.question_entity_type.entity_group.multi:
                to_delete = tree.question_entity_type.name
            validate_choice_and_save_from_response(tree, entities, user_id)
            validate_data_and_save_from_response(message, tree, user_id)
            print("Down")
            print(tree)
            (tree, pipe_temp) = returnNextTree(tree, user_id, pipe_temp, "post")
            print(tree)
            print("Down")
            user = Profile.objects.get(user_id=user_id)
            user.tree = tree
            user.stage = "pre"
            user.save()
            if to_delete != "":
                Data.objects.filter(entity_name=to_delete,
                                    user=user).delete()
            return process_any_tree_with_stages_new(tree, entities, user_id, flag, channel, message, what, pipe_temp)
    except Exception as e:
        logger.error(
            "Error process_any_tree_with_stages_new %s", str(e))

def get_random():
    try:
        logger.info("Entered get_random")
        objects = Recommendation.objects.all()
        list_temp = []
        for object in objects:
            list_temp.append(object.query_name)
        list_random = random.sample(list_temp, min(3, len(list_temp)))
        return (list_random)
    except Exception as e:
        logger.error("Error get_random %s", str(e))

def match_choices_final(tree, message, user_id, channel, language, clicked, pipe):
    try:
        json = {}
        clear_data_from_model(user_id)
        pipe_array = pipe.split("|")
        pipe_temp = ""
        for val in pipe_array[:len(pipe_array)-1]:
            json = match_choices_final_a(Profile.objects.get(user_id=user_id).tree, val, user_id, channel, language, clicked, pipe_temp)
            try:
                pipe_temp = json["pipe"]
            except:
                logger.info("no pipe")
        clear_data_from_model(user_id)
        reset_user(user_id)
        return json
    except Profile.DoesNotExist:
        logger.error("No matching profile found")

def save_to_log(channel, language, initial_message, user_id, answer_succesful, json):
    chatbot_answer = ""
    try:
        chatbot_answer = json["response"]
    except Exception as e:
        logger.error("function: match_choices_final No response %s", str(e))
    try:
        channel = Channel.objects.get(name=channel)
    except:
        channel = Channel(name=channel)
        channel.save()

    try:
        language = Language.objects.get(name=language)
    except:
        language = Language(name=language)
        language.save()

    Log(query=initial_message,
        user=Profile.objects.get(user_id=user_id),
        channel=channel,
        answer_succesfull=answer_succesful,
        chatbot_answer=chatbot_answer,
        language=language).save()

def match_choices_final_a(tree, message, user_id, channel, language):
    json = {}
    pipe_temp = ""
    answer_succesful = True
    initial_message = message
    print("Tree is ",tree)
    if tree is None:
        message = do_pre_processing(message, channel, language)
        print("AFTER PRE: ", message)

        entities = get_entity(message)
        intent = get_intent(message)
        logger.info("Intent is : %s", intent)
        logger.info("Entities is : %s", entities)
        print(intent, entities)
        recur_entity_tree(entities, user_id)
        current_query = increment_querycnt(message, channel)
        if intent is not None:
            intent_obj = get_object_or_404(Intent, name=intent[0].name)
            pipe_temp = add_entities_in_user(entities, intent_obj, current_query, user_id, pipe_temp)
            json = process_any_tree_with_stages_new(intent_obj.tree, entities, user_id, "false", channel, message,"true", pipe_temp)
        else:
            if entities is not None:
                recommendation_list = get_recommendation_list_from_entities(entities)
                (json, value) = get_recommendation_list_json(recommendation_list)

                answer_succesful = value
                if(value == False):
                    json["recommended_queries"] = get_random()
            else:
                answer_succesful = False
                json["is_typable"] = "true"
                message = str(Config.objects.all()[0].question_not_recognized)
                json["response"] = "I am sorry I could not help you. While I improve please contact customer service executive at our toll-free number 1800 425 3800."
                #json["recommended_queries"] = InitialBaseResponses()
    else:
        message = do_pre_processing(message, channel, language)
        print("AFTER PRE: ", message)
        intent = get_intent(message)
        print("Intent in else: ", intent)
        if intent is not None:
            entities = get_entity(message)
            recur_entity_tree(entities, user_id)
            current_query = increment_querycnt(message, channel)
            intent_obj = get_object_or_404(Intent, name=intent[0].name)
            pipe_temp = add_entities_in_user(entities, intent_obj, current_query, user_id, pipe_temp)
            json = process_any_tree_with_stages_new(intent_obj.tree, entities, user_id, "false", channel, message,"true", pipe_temp)
        else:
            message = message.lower()
            message = remove_nonalphanumeric(message)
            entities = get_entity(message)
            json = process_any_tree_with_stages_new(tree, entities, user_id, "false", channel, message, "false", pipe_temp)
    save_to_log(channel, language, initial_message, user_id, answer_succesful, json)
    return json

def Index(request):
    return render(request, 'engine/index.html', {})

def Iframe(request):
    return render(request, 'engine/chatbox.html', {})

def Analytics(request):
    return render(request, 'engine/analytics.html')

def parse_json(current_answer, file, user_id):
    if (file!="999abc999" and file is not None):
        try:
            current_answer = current_answer.replace("<p>","")
            current_answer = current_answer.replace("</p>", "")
            current_answer = current_answer.replace("&nbsp;", " ")
            file = Files.objects.get(file_name=file)
            df = pd.read_csv(file.file)
            string = ""
            flag_start = False
            word = ""
            flag_colon_start = False
            list = []
            list_to_find = []
            flag_start_2 = False
            for words in current_answer.split():
                if words == ")}":
                    flag_start_2 = False
                elif flag_start_2 == True:
                    list_to_find.append(words)
                elif words == "{(":
                    flag_start_2 = True
                elif words == "]}":
                    flag_start = False
                elif flag_start == True:
                    if flag_colon_start == True:
                        list_t = []
                        list_t.append(word)
                        list_t.append(words)
                        list.append(list_t)
                        flag_colon_start = False
                    if words == ":":
                        flag_colon_start=True
                    if flag_colon_start == False:
                        word = words
                elif words == "{[":
                    flag_start = True
                else:
                    string += words + " "

            for stuff in list:
                str1 = str(stuff[0])
                str2 = str(stuff[1])
                df[str1] = df[str1].astype(str)
                df[str1] = df[str1].str.lower()
                df = df.loc[df[str1] == str2.lower()]
            dict_temp = {}
            if(len(list_to_find)>0):
                for stuff in list_to_find:
                    if stuff == "respone_code":
                        if math.isnan(df.iloc[0][stuff]):
                            dict_temp[stuff] = "NaN"
                        else:
                            dict_temp[stuff] = int(df.iloc[0][stuff])
                    else:
                        dict_temp[stuff] = df.iloc[0][stuff]
            return (string, dict_temp)
        except:
            message = "Sorry the corresponding entry is not present in the database."
            return (message,{})
    else:
        return (current_answer, {})

def replace_values(sentence, dict_temp):
    sentence = sentence.replace("<p>", "")
    sentence = sentence.replace("</p>", "")
    sentence = sentence.replace("&nbsp;", " ")
    string = ""
    for words in sentence.split():
        if words in dict_temp:
            string += str(dict_temp[words]) + " "
        else:
            string += words + " "
    return string

def replace_if_statement(sentence):
    string = ""

    sentence = sentence.replace('<p>','')
    sentence = sentence.replace('</p>', '')
    string_answer_1 = ""
    string_answer_2 = ""
    condition = ""
    start_flag = False
    start_flag_2 = False
    start_flag_3 = False
    final_flag = False
    for words in sentence.split():
        #print(words)
        if words == "}}}":
            start_flag = False
        if start_flag == True:
            string_answer_1 += words + " "
        if words == "{{{":
            start_flag = True

        if words == "}}}}":
            start_flag_2 = False
        if start_flag_2 == True:
            string_answer_2 += words + " "
        if words == "{{{{":
            start_flag_2 = True

        if words == "))}":
            start_flag_3 = False
            final_flag = True
        if start_flag_3 == True:
            condition += words + " "
        if words == "{((":
            start_flag_3 = True

    condition = condition.replace(" ","")
    if final_flag == True:
        if condition!="nan":
            return string_answer_1
        else:
            return string_answer_2
    else:
        return sentence

def parse_api(message, user_id):
    try:
        string = ""
        final_string = ""
        flag_api = False
        for words in message.split():
            if words == "*}":
                flag_api = False
            elif flag_api == True:
                string += words + " "
            elif words == "{*":
                flag_api = True
            else:
                final_string += words + " "

        list = string.split(',')
        dict = {}
        temp_dict = {}
        for val in list:
            key, pair = val.split('[')
            if(key == "url"):
                dict["url"] = pair
            if(key == "type"):
                dict["type"] = pair
            if(key == "data"):
                pair = pair[1:]
                pair = pair[:-1]
                temp_list = pair.split(';')
                for item in temp_list:
                    keey, valuee = item.split("-")
                    temp_dict[keey] = valuee
                temp_dict["user_id"] = user_id
                dict["data"] = temp_dict
            if(key == "output"):
                pair = pair[1:]
                pair = pair[:-1]
                list = pair.split(';')
                dict["output"] = list

        if(dict["type"] == "GET"):
            a = requests.get(dict["url"])
        elif(dict["type"] == "POST"):
            answer = requests.post(dict["url"], dict["data"])

        answer = answer.json()

        for key, value in answer.items():
            for words in final_string.split():
                if words == key:
                    final_string = final_string.replace(words, str(value))

        return final_string
    except:
        return message

def calculate_age(born):
    today = dt.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def parse_super_json(sentence, user_id):
    try:
        sentence = sentence.replace("<p>", "")
        sentence = sentence.replace("</p>", "")
        sentence = sentence.replace("&nbsp;", " ")
        final_string = ""
        for words in sentence.split():
            if words == "**sumassured**":
                try:
                    date_of_birth = Data.objects.get(entity_name="DateOfBirth",
                                                        user__user_id=user_id).entity_value
                except:
                    date_of_birth = "19/10/1983"
                premium_years = Data.objects.get(entity_name="PremiumPeriod",
                                                    user__user_id=user_id).entity_value[:2]
                premium = Data.objects.get(entity_name="PremiumAmount",
                                              user__user_id=user_id).entity_value[4:]

                print("IMPORATANT")
                print(premium, premium_years, date_of_birth)
                date_of_birth_py = dt.strptime(date_of_birth,"%d/%m/%Y")
                age = int(calculate_age(date_of_birth_py))
                print(age)

                multiplier_factor = 0
                if int(premium_years) == 10:
                    if age >= 18 and age <=30:
                        multiplier_factor = 80
                    if age >=31 and age <=35:
                        multiplier_factor = 65
                    if age >=36 and age <=40:
                        multiplier_factor = 50
                    if age >=41 and age <=45:
                        multiplier_factor = 35
                    if age >=46 and age <=50:
                        multiplier_factor = 25
                    if age >=51 and age <=55:
                        multiplier_factor = 20
                if int(premium_years) == 15:
                    if age >= 18 and age <=30:
                        multiplier_factor = 95
                    if age >=31 and age <=35:
                        multiplier_factor = 70
                    if age >=36 and age <=40:
                        multiplier_factor = 55
                    if age >=41 and age <=45:
                        multiplier_factor = 40
                    if age >=46 and age <=50:
                        multiplier_factor = 30
                    if age >=51 and age <=55:
                        multiplier_factor = 20
                final_sum_assured = int(premium)*multiplier_factor
                print(final_sum_assured)
                locale.setlocale(locale.LC_MONETARY, 'en_IN')
                print("This is something ",locale.currency(final_sum_assured, grouping=True))
                final_string+=str(locale.currency(final_sum_assured, grouping=True))+" "
            else:
                final_string+=words+" "
        return final_string
    except:
        return sentence
        print("Error")


def parse_store_in_models(current_answer, file, user_id):
    try:
        if (file!="999abc999" and file is not None):
            try:
                current_answer = current_answer.replace("<p>","")
                current_answer = current_answer.replace("</p>", "")
                current_answer = current_answer.replace("&nbsp;", " ")
                file = Files.objects.get(file_name=file)
                df = pd.read_csv(file.file)
                string = ""
                flag_start = False
                word = ""
                flag_colon_start = False
                flag_colon_start_2 = False
                list = []
                list_to_find = []
                flag_start_2 = False
                for words in current_answer.split():
                    if words == ")}}":
                        flag_start_2 = False
                    elif flag_start_2 == True:
                        if flag_colon_start_2 == True:
                            list_t = []
                            list_t.append(word)
                            list_t.append(words)
                            list_to_find.append(list_t)
                            flag_colon_start_2 = False
                        if words == ":":
                            flag_colon_start_2=True
                        if flag_colon_start_2 == False:
                            word = words
                    elif words == "{{(":
                        flag_start_2 = True
                    elif words == "]}}":
                        flag_start = False
                    elif flag_start == True:
                        if flag_colon_start == True:
                            list_t = []
                            list_t.append(word)
                            list_t.append(words)
                            list.append(list_t)
                            flag_colon_start = False
                        if words == ":":
                            flag_colon_start=True
                        if flag_colon_start == False:
                            word = words
                    elif words == "{{[":
                        flag_start = True
                    else:
                        string += words + " "

                for stuff in list:
                    str1 = str(stuff[0])
                    str2 = str(stuff[1])
                    df[str1] = df[str1].astype(str)
                    df[str1] = df[str1].str.lower()
                    df = df.loc[df[str1] == str2.lower()]

                if(len(list_to_find)>0):
                    for stuff in list_to_find:
                        stuff_to_store = df.iloc[0][stuff[0]]
                        stuff_where_to_store = stuff[1]
                        Data(entity_name=stuff_where_to_store,
                             entity_value=stuff_to_store,
                             current_stage="Advisor Confidential Report",
                             user=Profile.objects.get(user_id=user_id)).save()
                return (string)
            except:
                message = "Sorry the corresponding entry is not present in the database."
                return (message)
        else:
            return (current_answer)
    except Exception as e:
        print("Exception is ", e)
def parse_sentence(current_answer, file , user_id):
    # Local Variables {@ @}
    # IsTypableVariables {/ /}
    # IsClickableVariables {+ +}
    # Excel/Json {[ ]} for value giving, {( )} for variables needed
    # if statment {(( condition_here ))} {{{ }}} {{{{ }}}}
    # API CALL {* url:url,type:type,data:{xxx-value;xxxy-value;},output{transaction_id;value} *}
    # parse_store_in_models {[ ]} for value giving {( for storing model name )}
    # e.g. {{[ production_number : {/ ProductionNumber /} ]}} {{[ parseNumber : Poop ]}}
    sentence = current_answer
    sentence = parse_is_typable(sentence, user_id)
    (sentence, dict_temp) = parse_json(sentence, file, user_id)
    sentence = replace_values(sentence, dict_temp)
    sentence = parse_super_json(sentence, user_id)
    sentence = parse_store_in_models(sentence, file, user_id)
    sentence = replace_if_statement(sentence)
    sentence = parse_api(sentence, user_id)
    return sentence

class MostSearchedQueriesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        queries = QueryCnt.objects.all().order_by('-count')
        top5queries = queries[:5]
        list = []
        for query in top5queries:
            dict = {}
            dict["question_asked"] = query.question_asked
            list.append(dict)
        return Response(data=list)

class OverallFeedbackAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        ##print(request.POST)
        data = request.data

        feedback = data.get('feedback')
        user_id = data.get('user_id')

        try:
            fdback = FeedbackGeneral.objects.filter(user_id=user_id).get()
            fdback.feedback = feedback
            fdback.save()
        except:
            fdback = FeedbackGeneral(user_id=user_id,
                                     feedback=feedback)
            fdback.save()

        return Response(data={})

def autocorrect(message, channel, language):
    if channel == "web" and language == "eng":
        try:
            logger.info("Entered autocorrect()")
            words_in_dict = list(AutoCorrectWordList.objects.all().values_list('word', flat=True))

            final_message = ''
            for index, elem in enumerate(message.split()):
                if len(elem) > 4:
                    if elem in words_in_dict:
                        final_message += elem + " "
                    else:
                        list_of_probable_words = []
                        for word in words_in_dict:
                            if (editdistance.eval(word, elem) <= 2):
                                list_of_probable_words.append(word)
                        if len(list_of_probable_words) > 0:
                            final_message += list_of_probable_words[0] + " "
                        else:
                            final_message += elem + " "
                else:
                    final_message += elem + " "
            return final_message
        except Exception as e:
            logger.error("Error in autocorrect() %s", str(e))

def remove_stopwords(message):
    try:
        logger.info("Entered remove_stopwords()")
        STOP_WORDS = set(STOPWORDS)
        list_t = []
        value = str(Config.objects.all()[0].custom_stop_word)
        for val in value.split(","):
            list_t.append(val)
        set_custom_stop_words = set(list_t)
        message = ' '.join([i for i in message.lower().split() if i not in STOP_WORDS])
        message = ' '.join([i for i in message.lower().split() if i not in set_custom_stop_words])
        return message
    except Exception as e:
        logger.error("Error in remove_stopwords %s", str(e))


# def get_entity(entity, intent):
#     temp = QueryList.objects.filter(entity=entity).exclude(intent=intent)
#     if temp.count() == 0:
#        return get_intent()
def recommendations(intent, entity):
    try:
        logger.info("Entered recommendations")
        intent_obj = intent
        entity_obj = entity
        if intent is not None and entity is not None:
            with_same_entity = Recommendation.objects.filter(entity=entity_obj).exclude(intent=intent_obj)
            if with_same_entity.count() == 0:
                with_same_entity = Recommendation.objects.filter(entity=entity_obj.parent)
            with_same_intent = Recommendation.objects.filter(intent=intent_obj).exclude(entity=entity_obj)

            list_with_same_entity = list(set(with_same_entity))
            list_with_same_intent = list(set(with_same_intent))

            if len(list_with_same_entity) > 3:
                list_random = random.sample(list_with_same_entity, 3)
            else:
                list_random = random.sample(list_with_same_entity, len(list_with_same_entity))
                more_needed_values = 3-len(list_random)
                if len(list_with_same_intent) > more_needed_values:
                    list_temp = random.sample(list_with_same_intent, more_needed_values)
                    list_random.extend(list_temp)
                else:
                    list_temp = random.sample(list_with_same_intent, len(list_with_same_intent))
                    list_random.extend(list_temp)
            list_query_name = []
            for elem in list_random:
                list_query_name.append(elem.query_name)
            return (list_query_name)

        elif entity is not None:
            objects = Recommendation.objects.filter(entity=entity_obj)

            list_temp = []
            for object in objects:
                list_temp.append(object.query_name)

            list_random = random.sample(list_temp, min(3, len(list_temp)))

            return (list_random)

        elif intent is not None:
            objects = Recommendation.objects.filter(intent=intent_obj)

            list_temp = []
            for object in objects:
                list_temp.append(object.query_name)

            list_random = random.sample(list_temp, min(3, len(list_temp)))

            return (list_random)
        return []
    except Exception as e:
        logger.error("Error in recommendations %s", str(e))
        return []
#
# def extract_value_from_initial_message(message, user_id):
#     try:
#         logger.info("Entered extract_value_from_initial_message")
#
#         functions = ValueExtracter.objects.all()
#
#         for function_t in functions:
#             function_string = function_t.valueextracter
#             d = {}
#             exec (str(function_string), d)
#
#             value = d['f'](message)
#
#             print("Evaluating: ", value)
#             if value is not None:
#                 entity_type_name = function_t.entitytype.type
#                 val_to_save = entity_type_name
#                 IsTypableData(entity_name=val_to_save,
#                               entity_value=value,
#                               user=Profile.objects.get(user_id=user_id)).save()
#     except Exception as e:
#         logger.error("Error from: extract_value_from_initial_message() %s", str(e))


def recur_entities(current_choice, user_id):
    try:
        logger.info("Entered recur_entities")
        parent = current_choice.parent
        for entity_type in parent.entity_choices.all():
            for question_entity_type in entity_type.question_group_set.all():
                val_to_save = question_entity_type.name
                Data(entity_name=val_to_save,
                     entity_value=parent.entity_name,
                     user=Profile.objects.get(user_id=user_id)).save()
        recur_entities(parent, user_id)
    except Exception as e:
        logger.error("Error from: recur_entities() %s", str(e))


def recur_entity_tree(entities, user_id):
    try:
        logger.info("Entered recur_entity_tree")
        for entity in entities:
            current_entity = Entities.objects.get(entity_name=entity.entity_name)
            recur_entities(current_entity, user_id)
    except Exception as e:
        logger.error("Error from: recur_entity_tree() %s", str(e))

def increment_querycnt(message, channel):
    try:
        query_cnt = QueryCnt.objects.get(query=message)
        cnt = query_cnt.count
        cnt = cnt + 1
        QueryCnt.objects.filter(query=message).update(count=cnt)
        current_query = query_cnt.pk
        return current_query
    except Exception as e:
        try:
            channel = Channel.objects.get(name="web")
        except:
            channel = Channel(name="web")
            channel.save()
        try:
            language = Language.objects.get(name="eng")
        except:
            language = Language(name="eng")
            language.save()
        query = QueryCnt(query=message,
                         channel=channel,
                         language=language,
                         count=0)
        query.save()
        logger.error("function: increment_quer_cnt %s", str(e))
        return query.pk

def add_entities_in_user(entities, intent_objects, query_id, user_id, pipe):
    try:
        user = Profile.objects.get(user_id=user_id)
        user.tree = intent_objects.tree
        pipe += intent_objects.name +"|"
        if entities is not None:
            for entity in entities:
                for entity_type in entity.entity_choices.all():
                    logger.info("Entity Name: %s", entity_type.name)
                    for question_entity_type in entity_type.question_group_set.all():
                        val_to_save = question_entity_type.name
                        Data(entity_name=val_to_save,
                             entity_value=entity.entity_name,
                             user=user).save()
        user.current_intent = intent_objects
        user.current_query = query_id
        user.save()
        return pipe
    except Profile.DoesNotExist:
        logger.error("No matching profile found")

def create_choice_list(entity_type):
    try:
        choices = entity_type.choices.all()
        choice_list = []
        for choice in choices:
            choice_list.append(choice.entity_name)
        return choice_list
    except Exception as e:
        logger.error("Error in: create_choice_list() %s", str(e))

def get_recommendation_list_from_entities(entities):
    try:
        recommendation_list = []
        for entity in entities:
            temp_list = recommendations(intent=None, entity=entity)
            recommendation_list.extend(temp_list)
        return recommendation_list
    except Exception as e:
        logger.error("Error in: get_recommendation_list_from_entities() %s", str(e))


def get_recommendation_list_json(recommendation_list):
    try:
        json = {}
        boolean = True
        if (len(recommendation_list) > 0):
            json["recommended_queries"] = recommendation_list
            message = str(Config.objects.all()[0].recommended_queries_statement)
            json["response"] = message
        else:
            message = str(Config.objects.all()[0].question_not_recognized)
            json["response"] = message
            boolean = False
        json["is_typable"] = "true"
        return (json, boolean)
    except Exception as e:
        logger.error("Error in: get_recommendation_list_json() %s", str(e))

def remove_nonalphanumeric(message):
    #pattern = re.compile('[^a-zA-Z0-9_ ]+', re.UNICODE)
    #pattern1 = re.compile("\s\s+", re.UNICODE)
    #message = pattern.sub('', message)
    #message = pattern1.sub(' ', message)
    #message = message.strip()
    #message = message.lower()
    return message

class CancelAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        json = {}
        json["is_typable"] = "true"

        user_id = data.get('user_id', False)

        clear_data_from_model(user_id)
        reset_user(user_id)

        json["response"] = Config.objects.all()[0].initial_message
        json["recommended_queries"] = InitialBaseResponses()
        return Response(data=json)

class QueryFeedbackLikeAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        data = self.kwargs
        user_id = data["user_id"]
        query_id = data["query_id"]
        try:
            fdback = QueryFeedbackCounter.objects.filter(user__user_id=user_id,
                                                  query__pk=query_id).get()
            fdback.like_cnt = 1
            if fdback.dislike_cnt == 1:
                fdback.dislike_cnt = 0
            fdback.save()
        except Exception as e:
            user = Profile.objects.get(user_id=user_id)
            QueryFeedbackCounter(user=user,
                          like_cnt=1,
                          query_id=query_id).save()
            logger.error("class: QueryFeedbackLikeAPIView, method: get %s", str(e))
        return Response(data={})

def parse_is_typable(current_answer, user_id):
    try:
        current_answer = current_answer.replace("<p>", "")
        current_answer = current_answer.replace("</p>", "")
        current_answer = current_answer.replace("&nbsp;", " ")
        flag_what = False
        string = ""
        for words in current_answer.split():
            if words == "/}":
                flag_what = False

            elif flag_what == True:
                variable_name = words
                obj = Data.objects.filter(entity_name=variable_name,
                                          user__user_id=user_id)
                count = obj.count()
                needed_obj = obj[count-1]
                value = needed_obj.entity_value
                if value:
                    string += value + " "

            elif words == "{/":
                flag_what = True
            else:
                string += words + " "
        #current_answer = current_answer.replace(" ","")
        #print("FINAL STRING IS", string)
        return string
    except:
        return "Corresponding entry is not present  "

def parse_all(sentence, user_id):
    try:
        model_name = 'Data'
        if '{@' not in sentence and '{/' not in sentence:
            return sentence
        if '{@' in sentence:
            model_name = 'Variables'
            first_index = sentence.index('@')-1
            temp_sentence = sentence
            temp_len = 0
            last_index = sentence.index('}')
            while True:
                if sentence[last_index-1] == '@':
                    break
                temp_len = last_index+1
                temp_sentence = sentence[last_index+1:]
                temp_len += temp_sentence.index('}')
                last_index = temp_len
        else:
            first_index = sentence.index('{')
            last_index = sentence.index('}')
        model_attribute = sentence[first_index+2:last_index-1]
        model_attribute = model_attribute.strip().lower()
        ret_value = ''
        if model_name == 'Variables':
            try:
                ret_value = Variables.objects.get(variable_name__iexact=model_attribute).variable_value
            except Variables.DoesNotExist:
                logger.error('function: parse_all Invalid Variable requested')
            except Exception as err:
                logger.error("function: parse_all Error: %s", str(err))
        else:
            try:
                ret_value = Data.objects.filter(entity_name__iexact=model_attribute, user__user_id=user_id).last().entity_value
            except Data.DoesNotExist:
                logger.error('function: parse_all Invalid IsTypableData requested')
            except Exception as err:
                logger.error("Error: %s", str(err))
        sentence = sentence[:first_index] + ret_value + sentence[last_index+1:]
        if '{/' in sentence or '{@' in sentence:
            sentence = parse_all(sentence, user_id)
        return sentence
    except Exception as e:
        logger.error("function: parse_all %s", str(e))
        return sentence

class QueryFeedbackDislikeAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        data = self.kwargs
        user_id = data["user_id"]
        query_id = data["query_id"]
        try:
            fdback = QueryFeedbackCounter.objects.filter(user__user_id=user_id,
                                                  query__pk=query_id).get()
            fdback.dislike_cnt = 1
            if fdback.like_cnt == 1:
                fdback.like_cnt = 0
            fdback.save()
        except Exception as e:
            QueryFeedbackCounter(user_id=user_id,
                          dislike_cnt=1,
                          query_id=query_id).save()
            logger.error("class: QueryFeedbackDislikeAPIView, method: get %s", str(e))
        return Response(data={})


class QueryAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data

        message = data.get('message', False)
        user_id = data.get('user_id', False)
        channel = data.get('channel', False)
        language = data.get('language', "eng")

        message = message.lower()

        user = Profile.objects.get(user_id=user_id)
        current_tree = user.tree

        print(message, "CHEEEEEEEEEEEEEEEEEEEEEEECK")

        json = match_choices_final_a(current_tree, message, user_id, channel, language)

        return Response(data=json)

def InitialBaseResponses():
    list_temp = []
    response_1 = Config.objects.all()[0].base_response_1
    if response_1 is not None:
        if response_1:
            list_temp.append(response_1)
    response_2 = Config.objects.all()[0].base_response_2
    if response_2 is not None:
        if response_2:
            list_temp.append(response_2)
    response_3 = Config.objects.all()[0].base_response_3
    if response_3 is not None:
        if response_3:
            list_temp.append(response_3)
    response_4 = Config.objects.all()[0].base_response_4
    if response_4 is not None:
        if response_4:
            list_temp.append(response_4)
    response_5 = Config.objects.all()[0].base_response_5
    if response_5 is not None:
        if response_5:
            list_temp.append(response_5)
    return list_temp

class UpdateUserAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        dict2 = {}
        dict2['user_id'] = data.get('user_id')
        Profile.objects.create(**dict2)
        json = {}
        json["is_typable"] = "true"
        json["response"] = Config.objects.all()[0].initial_message
        list_temp = InitialBaseResponses()
        json["recommended_queries"] = list_temp
        logger.info(json)
        return Response(data=json)

def createBlankDictionary(value, choice, start_date):
    dict = {}
    if choice == "0":
        current_date = start_date
        for i in range(value+1):
            t = current_date.strftime('%d/%m/%Y')
            dict[t] = 0
            current_date += timedelta(days=1)
    elif choice == "1":
        current_month = start_date.month - 1
        for i in range(value+1):
            current_month += 1
            if current_month == 13:
                current_month = 1
            dict[calendar.month_name[current_month]] = 0
    else:
        current_year = start_date.year
        for i in range(value+1):
            dict[current_year] = 0
            current_year += 1

    return dict

def returnChoice(date1, date2):
    delta = date2 - date1
    days = delta.days
    years, remainder = divmod(days, 365)
    months = years * 12 + (remainder // 30)

    # logger.info(days, months, years, remainder)

    if days > 0:
        if (years > 0):
            return (years, "2")
        elif (months > 0):
            return (months, "1")
        else:
            return (days, "0")

    return (days, "-1")


def Report(request, from_date, to_date):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sia_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Message Text',
        'Answered (Yes or No)',
        'user_id',
        'chatbot_answer'
    ])

    from_date = from_date.split("/")
    to_date = to_date.split("/")

    start_date = date(int(from_date[2]), int(from_date[1]), int(from_date[0]))
    end_date = date(int(to_date[2]), int(to_date[1]), int(to_date[0]))

    queries = Log.objects.filter(time__range=(start_date, end_date))

    for query in queries:
        if query.message_time is not None:
            ans = "No"
            if query.answer_succesfull:
                ans = "Yes"
            writer.writerow([
                smart_str(query.message_text),
                ans,
                smart_str(query.user.user_id),
                smart_str(query.chatbot_answer)
            ])

    return response

class GetPcIdAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        pc_id = data.get('pcid')

        try:
            UniqueUsers.objects.filter(user_id=pc_id).get()
        except Exception as e:
            p = UniqueUsers(user_id=pc_id)
            p.save()
        return Response(data={})

def get_top_intent_in_entities(entity_top_intent):
    TOP_Y_INTENT = 3
    top_intent_in_entities = {}
    for key, val in entity_top_intent.items():

        list_of_top_intents = val
        sorted_list = sorted(list_of_top_intents.items(), key=lambda x: -x[1])
        new_list_of_top_intents = {}
        for i in range(min(TOP_Y_INTENT, len(sorted_list))):
            new_list_of_top_intents[sorted_list[i][0]] = sorted_list[i][1]
        top_intent_in_entities[key] = new_list_of_top_intents

    return top_intent_in_entities

def get_top_entities_in_intent(intent_top_entity):
    TOP_Y_ENTITIES = 3
    top_entities_in_intent = {}
    for key, val in intent_top_entity.items():

        list_of_top_entities = val
        sorted_list = sorted(list_of_top_entities.items(), key=lambda x: -x[1])
        new_list_of_top_entities = {}
        for i in range(min(TOP_Y_ENTITIES, len(sorted_list))):
            new_list_of_top_entities[sorted_list[i][0]] = sorted_list[i][1]
        top_entities_in_intent[key] = new_list_of_top_entities

    return top_entities_in_intent


def get_entity_top_intent(analytics, entity_count_name):
    entity_top_intent = {}

    # Initializing for loop
    for analytic_obj in analytics:
        if analytic_obj.primary_entity is not None:
            if analytic_obj.primary_entity.choice_name not in entity_top_intent and analytic_obj.primary_entity.choice_name in entity_count_name:
                entity_top_intent[analytic_obj.primary_entity.choice_name] = {}

    # Filling for loop
    for analytic_obj in analytics:
        if analytic_obj.message_time is not None:
            if analytic_obj.primary_entity is not None and analytic_obj.primary_entity.choice_name in entity_top_intent:
                temp_dict = entity_top_intent[
                    analytic_obj.primary_entity.choice_name]
                if analytic_obj.intent is not None:
                    if analytic_obj.intent.name not in temp_dict:
                        temp_dict[analytic_obj.intent.name] = 1
                    else:
                        temp_dict[analytic_obj.intent.name] += 1
                entity_top_intent[
                    analytic_obj.primary_entity.choice_name] = temp_dict

    return entity_top_intent


def get_intent_top_entity(analytics):
    intent_top_entity = {}

    for analytic_obj in analytics:
        if analytic_obj.message_time is not None:
            if analytic_obj.intent is not None:
                if analytic_obj.intent.name not in intent_top_entity:
                    intent_top_entity[analytic_obj.intent.name] = {}
                temp_dict = intent_top_entity[analytic_obj.intent.name]
                if analytic_obj.primary_entity is not None:
                    if analytic_obj.primary_entity.choice_name not in temp_dict:
                        temp_dict[analytic_obj.primary_entity.choice_name] = 1
                    else:
                        temp_dict[analytic_obj.primary_entity.choice_name] += 1
                intent_top_entity[analytic_obj.intent.name] = temp_dict

    new_intent_top_entity = {}
    order_score = {}
    for key, val in intent_top_entity.items():
        if val:
            tot_val = sum(val.values())
            order_score[key] = tot_val

    sorted_intent = sorted(order_score.items(), key=lambda x: -x[1])
    sorted_intent = sorted_intent[-5:]

    new_intent_top_entity = dict((x, y) for x, y in sorted_intent)

    for i in sorted_intent:
        new_intent_top_entity[i[0]] = intent_top_entity[i[0]]

    return new_intent_top_entity


def get_total_unique_users(total_unique_users, unique_users, current_choice):
    for user in unique_users:
        t = user.message_time
        if current_choice == "0":
            total_unique_users[t.strftime('%d/%m/%Y')] += 1
        elif current_choice == "1":
            total_unique_users[calendar.month_name[t.month]] += 1
        else:
            total_unique_users[t.year] += 1

    return total_unique_users

def get_entity_count_and_entity_count_name(analytics):
    entity_count = {}

    for analytic_obj in analytics:
        if analytic_obj.message_time is not None:
            if analytic_obj.primary_entity is not None:
                if analytic_obj.primary_entity.choice_name not in entity_count:
                    entity_count[analytic_obj.primary_entity.choice_name] = 1
                else:
                    entity_count[analytic_obj.primary_entity.choice_name] += 1

    entity_count = sorted(entity_count.items(), key=lambda x: x[1])
    list = entity_count[-5:]
    entity_count_name = []
    entity_count = {}
    for key, val in list:
        entity_count[key] = val
        entity_count_name.append(key)

    return entity_count, entity_count_name

def get_final_average_dict(dict_user_cnt, dict_message_cnt, final_average_dict):
    for key, elem in final_average_dict.items():
        users = dict_user_cnt[key]
        messages = dict_message_cnt[key]

        if users != 0:
            average = messages / users
        else:
            average = 0
        final_average_dict[key] = average

    return final_average_dict


def get_dict_cnt(queries, current_choice, dict_message_cnt, dict_user_cnt):
    try:
        dict_user = {}
        for query in queries:
            if query.message_time is not None:
                t = query.message_time

                if current_choice == "0":
                    dict_message_cnt[t.strftime('%d/%m/%Y')] += 1
                    if query.user.user_id not in dict_user:
                        dict_user[query.user.user_id] = 1
                        dict_user_cnt[t.strftime('%d/%m/%Y')] += 1
                elif current_choice == "1":
                    dict_message_cnt[calendar.month_name[t.month]] += 1
                    if query.user.user_id not in dict_user:
                        dict_user[query.user.user_id] = 1
                        dict_user_cnt[calendar.month_name[t.month]] += 1
                else:
                    dict_message_cnt[t.year] += 1
                    if query.user.user_id not in dict_user:
                        dict_user[query.user.user_id] = 1
                        dict_user_cnt[t.year] += 1
    except Exception as e:
        logger.error(
            "class: GetAnalysisAPIView, method: post error %s", str(e))

    return dict_user_cnt, dict_message_cnt


class GetDictionaryAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        user_id = request.data.get('user_id','123')
        datas = Data.objects.filter(user__user_id=user_id)
        json = {}

        for data in datas:
            current_stage = data.current_stage
            current_entity_name = data.entity_name
            current_entity_value = data.entity_value

            redirect_intent = None
            if data.redirect_intent is not None:
                redirect_intent = data.redirect_intent
            entities_to_delete = None
            if data.redirect_entities_delete is not None:
                entities_to_delete = data.redirect_entities_delete
            if len(current_stage)>0:
                if current_stage not in json:
                    list = []
                    temp_dict = {}
                    temp_dict["entity_name"] = current_entity_name
                    temp_dict["entity_value"] = current_entity_value
                    temp_dict["redirect_intent"] = redirect_intent
                    temp_dict["entities_to_delete"] = entities_to_delete
                    list.append(temp_dict)
                    json[current_stage] = list
                else:
                    temp_dict = {}
                    temp_dict["entity_name"] = current_entity_name
                    temp_dict["entity_value"] = current_entity_value
                    temp_dict["redirect_intent"] = redirect_intent
                    temp_dict["entities_to_delete"] = entities_to_delete
                    json[current_stage].append(temp_dict)
        return Response(data=json)

class DeleteEntitiesAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data

        to_delete_entities = data.get('to_delete_entities').split(",")
        user_id = data.get('user_id')

        for entity in to_delete_entities:
            Data.objects.filter(entity_name=entity,
                                user__user_id=user_id).delete()

        user = Profile.objects.get(user_id=user_id)
        user.stage = "pre"
        user.save()

        return Response(data={})
class GetAnalysisAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):

        data = request.data

        from_date = data.get('from_date').split("/")
        to_date = data.get('to_date').split("/")

        start_date = date(int(from_date[2]),
                          int(from_date[1]),
                          int(from_date[0]))

        end_date = date(int(to_date[2]),
                        int(to_date[1]),
                        int(to_date[0]))

        choices = returnChoice(start_date, end_date)

        current_choice = choices[1]

        value = choices[0]

        dict_count = createBlankDictionary(value,
                                           current_choice,
                                           start_date)


        answered_count = createBlankDictionary(value,
                                               current_choice,
                                               start_date)

        unanswered_count = createBlankDictionary(value,
                                                 current_choice,
                                                 start_date)

        platform_dict = {}

        answered_messages = []
        unanswered_messages = []
        total_message = []

        dict_user_cnt = createBlankDictionary(value,
                                              current_choice,
                                              start_date)

        dict_message_cnt = createBlankDictionary(value,
                                                 current_choice,
                                                 start_date)

        final_average_dict = createBlankDictionary(value,
                                                   current_choice,
                                                   start_date)

        total_unique_users = createBlankDictionary(value,
                                                   current_choice,
                                                   start_date)

        queries = Log.objects.filter(
            time__range=(start_date, end_date))
        analytics = AnalyticCount.objects.filter(
            time__range=(start_date, end_date))
        unique_users = UniqueUsers.objects.filter(
            time__range=(start_date, end_date))

        list_insights_1 = {}
        clicked_vs_typed = {}
        try:
            for query in queries:

                if query.message_time is not None:
                    total_message.append(
                        query.message_text + " " + query.user.user_id)
                    if query.answer_succesfull == True:
                        answered_messages.append(
                            query.message_text + " " + query.user.user_id)
                    else:
                        unanswered_messages.append(
                            query.message_text + " " + query.user.user_id)
                    current_platform = query.platform
                    if current_platform != "False":
                        if current_platform not in platform_dict:
                            platform_dict[current_platform] = 1
                        else:
                            platform_dict[current_platform] += 1
                    clicked = query.clicked
                    if clicked == True:
                        if "clicked" not in clicked_vs_typed:
                            clicked_vs_typed["clicked"] = 1
                        else:
                            clicked_vs_typed["clicked"] += 1
                    else:
                        if "typed" not in clicked_vs_typed:
                            clicked_vs_typed["typed"] = 1
                        else:
                            clicked_vs_typed["typed"] += 1
                    t = query.message_time
                    if current_choice == "0":
                        dict_count[t.strftime('%d/%m/%Y')] += 1
                        if query.answer_succesfull == True:
                            answered_count[t.strftime('%d/%m/%Y')] += 1
                        else:
                            unanswered_count[t.strftime('%d/%m/%Y')] += 1
                    elif current_choice == "1":
                        dict_count[calendar.month_name[t.month]] += 1
                        if query.answer_succesfull == True:
                            answered_count[calendar.month_name[t.month]] += 1
                        else:
                            unanswered_count[calendar.month_name[t.month]] += 1
                    else:
                        dict_count[t.year] += 1
                        if query.answer_succesfull == True:
                            answered_count[t.year] += 1
                        else:
                            unanswered_count[t.year] += 1
                    list_insights_1["total_messages"] = dict_count
                    # print("It isisisisisisi ", list_insights_1["total_messages"])
                    list_insights_1["answered_messages"] = answered_count
                    list_insights_1["unanswered_messages"] = unanswered_count
        except Exception as e:
            logger.error(
                "class: GetAnalysisAPIView, method: post ERROr %s", str(e))

        dict_user_cnt, dict_message_cnt = get_dict_cnt(queries,
                                                       current_choice,
                                                       dict_message_cnt,
                                                       dict_user_cnt)

        final_average_dict = get_final_average_dict(dict_user_cnt,
                                                    dict_message_cnt,
                                                    final_average_dict)

        (entity_count,
         entity_count_name) = get_entity_count_and_entity_count_name(analytics)

        entity_top_intent = get_entity_top_intent(analytics, entity_count_name)

        top_intent_in_entities = get_top_intent_in_entities(entity_top_intent)

        intent_top_entity = get_intent_top_entity(analytics)

        top_entities_in_intent = get_top_entities_in_intent(intent_top_entity)

        total_unique_users = get_total_unique_users(total_unique_users,
                                                    unique_users,
                                                    current_choice)

        final_dict = {}

        final_dict["list_insights_1"] = list_insights_1
        final_dict["platform_dict"] = platform_dict
        final_dict["average_session_time"] = final_average_dict
        final_dict["clicked_vs_typed"] = clicked_vs_typed
        final_dict["top_products"] = entity_count
        final_dict["top_intent_in_entities"] = top_intent_in_entities
        final_dict["top_entities_in_intent"] = top_entities_in_intent
        final_dict["total_unique_users"] = total_unique_users
        final_dict["answered_messages"] = answered_messages
        final_dict["unanswered_messages"] = unanswered_messages
        final_dict["total_messages"] = total_message

        return Response(data=final_dict)


UpdateUser = UpdateUserAPIView.as_view()
Querys = QueryAPIView.as_view()
Cancel = CancelAPIView.as_view()
QueryFeedbackLike = QueryFeedbackLikeAPIView.as_view()
QueryFeedbackDislike = QueryFeedbackDislikeAPIView.as_view()
GetAnalysis = GetAnalysisAPIView.as_view()
GetPcId = GetPcIdAPIView.as_view()
GetDictionary = GetDictionaryAPIView.as_view()
deleteEntities = DeleteEntitiesAPIView.as_view()
#-----------------------------------------------------------------------------------------------------------------------
# UNUSED FUNCTIONS WHICH I ONCE MADE WHICH ARE REALLY IMPORTANT BUT NO ONE USES IT :( :( :(
#-----------------------------------------------------------------------------------------------------------------------


# Autosuggest.
    # Simple prefix match version
        #     def get_prefix_matches(prev_word,query):
        #     list = []
        #
        #     (dicti, words_in_dict) = load_the_dictionary()
        #
        #     print(words_in_dict, "Words in dictionary")
        #     if(query!=""):
        #         for word in words_in_dict:
        #             if word.startswith(query):
        #                 list.append(word)
        #     print(list)
        #

    # Bigram Version
        # def load_the_dictionary():
        #    words_in_dict = set(
        #        KnowledgeBase.objects.all().values_list('word', flat=True))
        #    dictionary = list(
        #        KnowledgeBase.objects.all().values_list('word', flat=True))
        #    return (dictionary, words_in_dict)
        #
        # def get_prefix_matches(prev_word,query):
        #     list = []
        #
        #     (dicti, words_in_dict) = load_the_dictionary()
        #
        #     #print(words_in_dict, "Words in dictionary")
        #     #if(query!=""):
        #     #    for word in words_in_dict:
        #     #        if word.startswith(query):
        #     #            list.append(word)
        #     ##print(list)
        #
        #     #words_in_dict = list(KnowledgeBase.objects.all().values_list('word', flat=True))
        #     #words_in_dict = set(GoodWords.objects.all().values_list('word', flat=True))
        #
        #     elem = query
        #     #list_message = list(message.split())
        #
        #     #final_message = ''
        #     if(elem!=""):
        #         if elem in words_in_dict:
        #             list.append(elem)
        #         else:
        #             possible_words = Bigrams.objects.filter(word1=prev_word).order_by('-cnt')
        #
        #             try:
        #                 flag = 0
        #                 for word in possible_words:
        #                     if word.word2.startswith(elem):
        #                         flag = 1
        #                         list.append(word.word2)
        #
        #                 if flag == 0:
        #                     for word in words_in_dict:
        #                         if word.startswith(elem):
        #                             list.append(word)
        #             except:
        #                 for word in words_in_dict:
        #                     if word.startswith(elem):
        #                         list.append(word)
        #
        #     ##print(prev_word, possible_words)
        #     ##print(final_message)
        #     return list

# Autocorrect with bigrams:

    # def autocorrect(message):
    #     words_in_dict = list(GoodWords.objects.all().values_list('word', flat=True))
    #     list_message = list(message.split())
    #
    #     final_message = ''
    #     for index,elem in enumerate(message.split()):
    #         if elem != "check":
    #             if len(elem) > 4:
    #                 if elem in words_in_dict:
    #                     final_message += elem
    #                     final_message += ' '
    #                 else:
    #                     list_of_probable_words = []
    #
    #                     for word in words_in_dict:
    #                         if (editdistance.eval(word, elem) <= 2):
    #                             list_of_probable_words.append(word)
    #
    #                     if len(list_of_probable_words)>0:
    #                         final_message += list_of_probable_words[0] + " "
    #                     else:
    #                         final_message += elem + " "
    #             else:
    #                 final_message += elem + " "
    #             # if index == 0:
    #             #     prev_word = "null"
    #             # else:
    #             #     prev_word = list_message[index-1]
    #             #
    #             # possible_words = Bigrams.objects.filter(word1=prev_word,word2__in=list_of_probable_words).order_by('-cnt')
    #             #
    #             # try:
    #             #     obj = possible_words[0]
    #             #     list_message[index] = obj.word2
    #             #     final_message += obj.word2
    #             #     final_message += ' '
    #             # except Exception as e:
    #             #     final_message += elem
    #             #     final_message += ' '
    #
    #     print(final_message, "Final Message::::::::::::::::::::::::::::")
    #     return final_message

# Extract value from initial hsbc specific
    # def extract_value_from_initial_message_hsbc_specific(message,user_id):
    #     try:
    #         print("REACHED1")
    #         cheque_extracter = ValueExtracter.objects.get(entitytype__type="HSBC@Cheque")
    #         transaction_extracter = ValueExtracter.objects.get(entitytype__type="HSBC@Transaction")
    #         customer_accnt_extracter = ValueExtracter.objects.get(entitytype__type="HSBC@CustomerAccountNumber")
    #         customer_code = ValueExtracter.objects.get(entitytype__type="HSBC@CustomerCode")
    #         print("REACHED2")
    #         cheque_flag = False
    #         transact_flag = False
    #         customer_account_number = False
    #         customer_code_flag = False
    #         print("REACHED3")
    #         for words in message.split():
    #             print("REACHED4", words, cheque_flag, transact_flag, customer_account_number)
    #             if customer_code_flag == True:
    #                 func_string = customer_code.valueextracter
    #                 d = {}
    #                 exec (str(func_string), d)
    #
    #                 value = d['f'](words)
    #                 print(str(func_string), words, value, "Customer code")
    #                 if value is not None:
    #                     IsTypableData(entity_name=customer_code.entitytype,
    #                                   entity_value=value.upper(),
    #                                   user=Profile.objects.get(user_id=user_id)).save()
    #                     customer_code = False
    #             elif customer_account_number == True:
    #                 func_string = customer_accnt_extracter.valueextracter
    #                 d={}
    #                 exec(str(func_string), d)
    #
    #                 value = d['f'](words)
    #                 print(str(func_string), words, value, "Customer account")
    #                 if value is not None:
    #                     IsTypableData(entity_name=customer_accnt_extracter.entitytype,
    #                                   entity_value=value,
    #                                   user=Profile.objects.get(user_id=user_id)).save()
    #                     customer_account_number = False
    #             elif transact_flag == True:
    #                 func_string = transaction_extracter.valueextracter
    #                 d={}
    #                 exec(str(func_string), d)
    #                 value = d['f'](words)
    #
    #                 if value is not None:
    #                     IsTypableData(entity_name=transaction_extracter.entitytype,
    #                                   entity_value=value,
    #                                   user=Profile.objects.get(user_id=user_id)).save()
    #                     transact_flag = False
    #             elif cheque_flag == True:
    #                 func_string = cheque_extracter.valueextracter
    #                 d={}
    #                 exec(str(func_string), d)
    #
    #                 value = d['f'](words)
    #                 print(str(func_string), words, value, "Cheque number")
    #                 if value is not None:
    #                     IsTypableData(entity_name=cheque_extracter.entitytype,
    #                                   entity_value=value,
    #                                   user=Profile.objects.get(user_id=user_id)).save()
    #                     cheque_flag = False
    #             if words == "cheque":
    #                 cheque_flag = True
    #             if words == "transaction":
    #                 transact_flag = True
    #             if words == "account":
    #                 customer_account_number = True
    #             if words == "code":
    #                 customer_code_flag = True
    #     except:
    #         print("Error from: extract_value_from_initial_message()")


# Execute activity
    # def execute_activity(tree):
    #     try:
    #         activity = tree.activity
    #         if (activity != ""):
    #             d = {}
    #             exec (activity, d)
    #     except:
    #         print("Error in: execute_activity()")
