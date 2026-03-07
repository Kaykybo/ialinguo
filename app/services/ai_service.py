import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY', 'sua-chave-aqui')


class AIService:

    CONTEXTOS = {
        'restaurante': "You are a restaurant waiter in an English-speaking country. Be polite and help the customer with orders, menu questions, etc. Respond only in English.",
        'academia': "You are a personal trainer at a gym in the USA. Talk about exercises, workout routines, health tips. Respond only in English.",
        'aeroporto': "You are an airport employee. Help the passenger with check-in, flight information, boarding gates. Respond only in English.",
        'hotel': "You are a hotel receptionist. Help with reservations, check-in, check-out, hotel information. Respond only in English.",
        'entrevista': "You are a recruiter conducting a job interview in English. Ask professional questions about experience, skills, etc.",
        'conversa livre': "You are a native English friend chatting casually. Keep the conversation natural and friendly. Respond only in English."
    }

    def _get_system_prompt(self, contexto):
        return self.CONTEXTOS.get(contexto, self.CONTEXTOS['conversa livre'])

    def _montar_messages(self, mensagem_aluno, contexto, historico):
        messages = [{"role": "system", "content": self._get_system_prompt(contexto)}]

        for msg in historico[-5:]:
            role = "user" if msg['remetente'] == 'aluno' else "assistant"
            messages.append({"role": role, "content": msg['texto']})

        messages.append({"role": "user", "content": mensagem_aluno})
        return messages

    def gerar_resposta(self, mensagem_aluno, contexto='conversa livre', historico=[]):
        try:
            messages = self._montar_messages(mensagem_aluno, contexto, historico)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Erro na API OpenAI: {e}")
            return "I'm sorry, I'm having trouble responding right now. Please try again."

    def gerar_feedback(self, conversa_texto, contexto):
        try:
            prompt = f"""
            Analyze the following English conversation of a Brazilian student learning English.
            Conversation context: {contexto}
            
            Conversation:
            {conversa_texto}
            
            Provide structured feedback in JSON with:
            1. pontos_positivos: What the student did well (grammar, vocabulary, fluency)
            2. pontos_melhoria: What needs improvement
            3. nota_fluencia: A score from 1 to 10
            4. dicas: 2-3 specific tips for improvement
            
            Respond only with valid JSON.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an English teacher specializing in feedback for Brazilian students."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Erro ao gerar feedback: {e}")
            return {
                "pontos_positivos": "You practiced English conversation.",
                "pontos_melhoria": "Keep practicing to improve.",
                "nota_fluencia": 5,
                "dicas": ["Practice more", "Listen to native speakers", "Repeat out loud"]
            }
