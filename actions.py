from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import openai
import os
from rasa_sdk.types import DomainDict
    
class ActionFillMobilityMessages(Action):
    def name(self) -> Text:
        return "action_fill_mobility_messages"

class ActionCategorizeMobility(Action):
    def name(self) -> Text:
        return "action_categorize_mobility"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        # Get the mobility response of user
        user_response = tracker.latest_message.get('text')
        current_list = tracker.get_slot('mobility_messages') or []
        question = "Bot: Hoe is uw mobiliteit vandaag"
        current_list+=[question, f"Gebruiker: {user_response}"]

        # OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

        chat_history = "\n".join(current_list)

        # Construct the prompt for the GPT model
        prompt = f"""
        Lees het volgende gesprek tussen tussen gebruiker en chatbot:
        {chat_history}

        Categorizeer de mobiliteit van de gebruiker in 1 van deze categorieën:
        1. Ik heb geen problemen met lopen
        2. Ik heb een beetje problemen met lopen
        3. Ik heb matige problemen met lopen
        4. Ik heb ernstige problemen met lopen
        5. Ik ben niet in staat om te lopen

        Antwoord alleen met het getal van de categorie en niks anders.
        """

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een behulpzame assistent."},  # System role to set behavior
                    {"role": "user", "content": prompt},  # User role with the actual prompt
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.5,
                logprobs=True
            )

            choice = response['choices'][0]
            categorized_response = choice['message']['content'].strip()
            category = int(categorized_response[0])
            print(category)
            log=choice['logprobs']['content'][0]['logprob'] #get logprobability
            print(log)
            
            if log>(-0.01):
                return [SlotSet("mobility_confidence", True), SlotSet("mobility_level", category), SlotSet("follow_up_question", None)]
            else:
                # Construct the prompt for the GPT model to generate a conversational follow-up question
                followup_prompt = f"""
                Je bent een vriendelijk en behulpzame assistent. Lees het volgende gesprek tussen gebruiker en chatbot:
                {chat_history}
                Erken de laatste reactie van de gebruiker en reageer of een natuurlijke en 
                empatische manier. Stel aan de hand van het gevoerde gesprek een gerichte vervolgvraag om meer informatie 
                over de mobiliteit van de gebruiker te krijgen, zodat het beter gecategoriseerd kan worden in 1 van de volgende categorieën: 

                1. Ik heb geen problemen met lopen
                2. Ik heb een beetje problemen met lopen
                3. Ik heb matige problemen met lopen
                4. Ik heb ernstige problemen met lopen
                5. Ik ben niet in staat om te lopen

                Geef antwoord zonder "Bot:" ervoor te zetten.
                """

                # Call the OpenAI API to generate a follow-up question
                followup_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly and helpful assistant."},
                        {"role": "user", "content": followup_prompt},
                    ],
                    max_tokens=120,
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                followup_choice = followup_response['choices'][0]
                followup_question = followup_choice['message']['content'].strip()
                current_list+=[f"Bot: {followup_question}"]

                return [SlotSet("mobility_messages", current_list), SlotSet("mobility_confidence", False), SlotSet("follow_up_question", followup_question), SlotSet("follow_up_mobility", None)]

        except Exception as e:
                dispatcher.utter_message(text="Sorry, I couldn't categorize your response at the moment. Please try again later.")

        

class ActionCategorizeSelfcare(Action):
    def name(self) -> Text:
        return "action_categorize_selfcare"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        # Get the selfcare response of user
        user_response = tracker.latest_message.get('text')
        current_list = tracker.get_slot('selfcare_messages') or []
        question = "Bot: Hoe gaat het met uw zelfzorg vandaag (jezelf wassen en aankleden bijvoorbeeld)"
        current_list+=[question, f"Gebruiker: {user_response}"]

        # OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

        chat_history = "\n".join(current_list)

        print(chat_history)

        # Construct the prompt for the GPT model
        prompt = f"""
        Lees het volgende gesprek tussen tussen gebruiker en chatbot:
        {chat_history}

        Categorizeer de zelfzorg van de gebruiker in 1 van deze categorieën:
        1. Ik heb geen problemen mezelf te wassen en aan te kleden
        2. Ik heb een beetje problemen mezelf te wassen en aan te kleden
        3. Ik heb matige problemen met mezelf te wassen en aan te kleden
        4. Ik heb ernstige problemen met mezelf te wassen en aan te kleden
        5. Ik ben niet in staat om mezelf te wassen en aan te kleden

        Antwoord alleen met het getal van de categorie en niks anders.
        """

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een behulpzame assistent."},  # System role to set behavior
                    {"role": "user", "content": prompt},  # User role with the actual prompt
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.2,
                logprobs=True
            )

            choice = response['choices'][0]
            categorized_response = choice['message']['content'].strip()
            category = int(categorized_response[0])
            print(category)
            log=choice['logprobs']['content'][0]['logprob'] #get logprobability
            print(log)
            
            if log>(-0.01):
                return [SlotSet("selfcare_confidence", True), SlotSet("selfcare_level", category), SlotSet("follow_up_question", None)]
            else:
                # Construct the prompt for the GPT model to generate a conversational follow-up question
                followup_prompt = f"""
                Je bent een vriendelijk en behulpzame assistent. Lees het volgende gesprek tussen gebruiker en chatbot:
                {chat_history}
                Erken de laatste reactie van de gebruiker en reageer of een natuurlijke en 
                empatische manier. Stel aan de hand van het gevoerde gesprek een gerichte vervolgvraag om meer informatie 
                over de zelfzorg van de gebruiker te krijgen, zodat het beter gecategoriseerd kan worden in 1 van de volgende categorieën: 

                1. Ik heb geen problemen mezelf te wassen en aan te kleden
                2. Ik heb een beetje problemen mezelf te wassen en aan te kleden
                3. Ik heb matige problemen met mezelf te wassen en aan te kleden
                4. Ik heb ernstige problemen met mezelf te wassen en aan te kleden
                5. Ik ben niet in staat om mezelf te wassen en aan te kleden

                Geef antwoord zonder "Bot:" ervoor te zetten.
                """

                # Call the OpenAI API to generate a follow-up question
                followup_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly and helpful assistant."},
                        {"role": "user", "content": followup_prompt},
                    ],
                    max_tokens=120,
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                followup_choice = followup_response['choices'][0]
                followup_question = followup_choice['message']['content'].strip()
                current_list+=[f"Bot: {followup_question}"]

                return [SlotSet("selfcare_messages", current_list), SlotSet("selfcare_confidence", False), SlotSet("follow_up_question", followup_question), SlotSet("follow_up_selfcare", None)]

        except Exception as e:
                dispatcher.utter_message(text="Sorry, I couldn't categorize your response at the moment. Please try again later.")
    
class ActionCategorizeActivity(Action):
    def name(self) -> Text:
        return "action_categorize_activity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        # Get the activities response of user
        user_response = tracker.latest_message.get('text')
        current_list = tracker.get_slot('activity_messages') or []
        question = "Bot: Hoeveel problemen ervaart u met dagelijkse activiteiten zoals, werk, studie, huishouden, gezins- of vrijetijdsactiviteiten?"
        current_list+=[question, f"Gebruiker: {user_response}"]

        # OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

        chat_history = "\n".join(current_list)

        # Construct the prompt for the GPT model
        prompt = f"""
        Lees het volgende gesprek tussen tussen gebruiker en chatbot:
        {chat_history}

        Categorizeer aan de hand van het gesprek de gebruiker in 1 van deze categorieën:
        1. Ik heb geen problemen met het uitvoeren van dagelijkse activiteiten
        2. Ik heb een beetje problemen met het uitvoeren van dagelijkse activiteiten
        3. Ik heb matige problemen met het uitvoeren van dagelijkse activiteiten
        4. Ik heb ernstige problemen met het uitvoeren van dagelijkse activiteiten
        5. Ik ben niet in staat om dagelijkse activiteiten uit te voeren

        Antwoord alleen met het getal van de categorie en niks anders.
        """

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een behulpzame assistent."},  # System role to set behavior
                    {"role": "user", "content": prompt},  # User role with the actual prompt
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.2,
                logprobs=True
            )

            choice = response['choices'][0]
            categorized_response = choice['message']['content'].strip()
            category = int(categorized_response[0])
            print(category)
            log=choice['logprobs']['content'][0]['logprob'] #get logprobability
            print(log)
            
            if log>(-0.01):
                return [SlotSet("activity_confidence", True), SlotSet("activity_level", category), SlotSet("follow_up_question", None)]
            else:
                # Construct the prompt for the GPT model to generate a conversational follow-up question
                followup_prompt = f"""
                Je bent een vriendelijk en behulpzame assistent. Lees het volgende gesprek tussen gebruiker en chatbot:
                {chat_history}
                Erken de laatste reactie van de gebruiker en reageer of een natuurlijke en 
                empatische manier. Stel aan de hand van het gevoerde gesprek een gerichte vervolgvraag om meer informatie 
                over het uitvoeren van dagelijkse activiteiten door de gebruiker te krijgen, 
                zodat het beter gecategoriseerd kan worden in 1 van de volgende categorieën:

                1. Ik heb geen problemen met het uitvoeren van dagelijkse activiteiten
                2. Ik heb een beetje problemen met het uitvoeren van dagelijkse activiteiten
                3. Ik heb matige problemen met het uitvoeren van dagelijkse activiteiten
                4. Ik heb ernstige problemen met het uitvoeren van dagelijkse activiteiten
                5. Ik ben niet in staat om dagelijkse activiteiten uit te voeren

                Geef antwoord zonder "Bot:" ervoor te zetten.
                """

                # Call the OpenAI API to generate a follow-up question
                followup_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly and helpful assistant."},
                        {"role": "user", "content": followup_prompt},
                    ],
                    max_tokens=120,
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                followup_choice = followup_response['choices'][0]
                followup_question = followup_choice['message']['content'].strip()
                current_list+=[f"Bot: {followup_question}"]

                return [SlotSet("activity_messages", current_list), SlotSet("activity_confidence", False), SlotSet("follow_up_question", followup_question), SlotSet("follow_up_activity", None)]

        except Exception as e:
                dispatcher.utter_message(text="Sorry, I couldn't categorize your response at the moment. Please try again later.")
    

class ActionCategorizePain(Action):
    def name(self) -> Text:
        return "action_categorize_pain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

         # Get the pain response of user
        user_response = tracker.latest_message.get('text')
        current_list = tracker.get_slot('pain_messages') or []
        question = "Bot: Hoeveel pijn of ongemak voelt u?"
        current_list+=[question, f"Gebruiker: {user_response}"]

        # OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

        chat_history = "\n".join(current_list)

        # Construct the prompt for the GPT model
        prompt = f"""
        Lees het volgende gesprek tussen tussen gebruiker en chatbot:
        {chat_history}

        Categorizeer aan de hand van het gesprek de gebruiker in 1 van deze categorieën:
        1. Ik heb geen pijn of ongemak
        2. Ik heb een beetje pijn of ongemak
        3. Ik heb matige pijn of ongemak
        4. Ik heb ernstige pijn of ongemak
        5. Ik heb extreme pijn of ongemak

        Antwoord alleen met het getal van de categorie en niks anders.
        """

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een behulpzame assistent."},  # System role to set behavior
                    {"role": "user", "content": prompt},  # User role with the actual prompt
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.2,
                logprobs=True
            )

            choice = response['choices'][0]
            categorized_response = choice['message']['content'].strip()
            category = int(categorized_response[0])
            print(category)
            log=choice['logprobs']['content'][0]['logprob'] #get logprobability
            print(log)
            
            if log>(-0.01):
                return [SlotSet("pain_confidence", True), SlotSet("pain_level", category), SlotSet("follow_up_question", None)]
            else:
                # Construct the prompt for the GPT model to generate a conversational follow-up question
                followup_prompt = f"""
                Je bent een vriendelijk en behulpzame assistent. Lees het volgende gesprek tussen gebruiker en chatbot:
                {chat_history}
                 Erken de laatste reactie van de gebruiker en reageer of een natuurlijke en 
                empatische manier. Stel aan de hand van het gevoerde gesprek een gerichte vervolgvraag om meer informatie 
                over de pijn en ongemak van de gebruiker te krijgen, zodat het beter gecategoriseerd kan worden in 1 van de volgende categorieën:
                
                1. Ik heb geen pijn of ongemak
                2. Ik heb een beetje pijn of ongemak
                3. Ik heb matige pijn of ongemak
                4. Ik heb ernstige pijn of ongemak
                5. Ik heb extreme pijn of ongemak
                
                Geef antwoord zonder "Bot:" ervoor te zetten.
                """

                # Call the OpenAI API to generate a follow-up question
                followup_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly and helpful assistant."},
                        {"role": "user", "content": followup_prompt},
                    ],
                    max_tokens=120,
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                followup_choice = followup_response['choices'][0]
                followup_question = followup_choice['message']['content'].strip()
                current_list+=[f"Bot: {followup_question}"]

                return [SlotSet("pain_messages", current_list), SlotSet("pain_confidence", False), SlotSet("follow_up_question", followup_question), SlotSet("follow_up_pain", None)]

        except Exception as e:
                dispatcher.utter_message(text="Sorry, I couldn't categorize your response at the moment. Please try again later.")
    
class ActionCategorizeAnxiety(Action):
    def name(self) -> Text:
        return "action_categorize_anxiety"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

         # Get the anxiety response of user
        user_response = tracker.latest_message.get('text')
        current_list = tracker.get_slot('anxiety_messages') or []
        question = "Bot: Hoe angstig of somber voelt u zich?"
        current_list+=[question, f"Gebruiker: {user_response}"]

        # OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

        chat_history = "\n".join(current_list)

        # Construct the prompt for the GPT model
        prompt = f"""
        Lees het volgende gesprek tussen tussen gebruiker en chatbot:
        {chat_history}

        Categorizeer aan de hand van het gesprek de gebruiker in 1 van deze categorieën:
        1. Ik ben niet angstig of somber
        2. Ik ben een beetje angstig of somber
        3. Ik ben matig angstig of somber
        4. Ik ben ernstig angstig of somber
        5. Ik ben extreem angstig of somber

        Let op! Antwoord alleen met het getal van de categorie en niks anders. Ik heb namelijk alleen het getal nodig.
        """

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een behulpzame assistent."},  # System role to set behavior
                    {"role": "user", "content": prompt},  # User role with the actual prompt
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.2,
                logprobs=True
            )

            choice = response['choices'][0]
            categorized_response = choice['message']['content'].strip()
            category = int(categorized_response[0])
            print(category)
            log=choice['logprobs']['content'][0]['logprob'] #get logprobability
            print(log)
            
            if log>(-0.01):
                return [SlotSet("anxiety_confidence", True), SlotSet("anxiety_level", category), SlotSet("follow_up_question", None)]
            else:
                # Construct the prompt for the GPT model to generate a conversational follow-up question
                followup_prompt = f"""
                Je bent een vriendelijk en behulpzame assistent. Lees het volgende gesprek tussen gebruiker en chatbot:
                {chat_history}
                Erken de laatste reactie van de gebruiker en reageer of een natuurlijke en 
                empatische manier. Stel aan de hand van het gevoerde gesprek een gerichte vervolgvraag om meer informatie 
                over de angstigheid en somberheid van de gebruiker te krijgen, zodat het beter gecategoriseerd kan worden in 1 van de volgende categorieën:
                
                1. Ik ben niet angstig of somber
                2. Ik ben een beetje angstig of somber
                3. Ik ben matig angstig of somber
                4. Ik ben ernstig angstig of somber
                5. Ik ben extreem angstig of somber

                Geef antwoord zonder "Bot:" ervoor te zetten.
                """

                # Call the OpenAI API to generate a follow-up question
                followup_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly and helpful assistant."},
                        {"role": "user", "content": followup_prompt},
                    ],
                    max_tokens=120,
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                followup_choice = followup_response['choices'][0]
                followup_question = followup_choice['message']['content'].strip()
                current_list+=[f"Bot: {followup_question}"]

                return [SlotSet("anxiety_messages", current_list), SlotSet("anxiety_confidence", False), SlotSet("follow_up_question", followup_question), SlotSet("follow_up_anxiety", None)]

        except Exception as e:
                dispatcher.utter_message(text="Sorry, I couldn't categorize your response at the moment. Please try again later.")
