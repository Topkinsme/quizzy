import os
import django
import tracemalloc
import uuid
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from asgiref.sync import sync_to_async
import random

from dotenv import load_dotenv

load_dotenv()

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizzy.settings')
django.setup()

# Start tracing memory allocations
tracemalloc.start()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from website.models import Quiz, Question, Participant

BOT_TOKEN = "" #os.getenv("BOT_TOKEN") # Replace with your actual token
QUIZ_CODE, USER_NAME, ANSWER = range(3)

chars = [chr(x) for x in range(65, 91)]
nums = [chr(x) for x in range(48, 58)]

def generategeneric():
    return random.choice(chars) + random.choice(chars) + random.choice(nums) + random.choice(nums) + random.choice(chars) + random.choice(chars)

def generate_participant_id():
    code = generategeneric()
    while Participant.objects.filter(p_id=code).exists():
        code = generategeneric()
    return code

@sync_to_async
def get_quiz_by_code(quiz_code):
    try:
        return Quiz.objects.get(quiz_id=quiz_code)
    except Quiz.DoesNotExist:
        return None

@sync_to_async
def create_participant(name, quiz_id):
    participant_id = generate_participant_id()
    participant = Participant.objects.create(p_id=participant_id, name=name, quiz_id=quiz_id)
    return participant

@sync_to_async
def get_questions(quiz_id):
    return list(Question.objects.filter(parent=quiz_id))

@sync_to_async
def save_participant_answers(participant_id, answers):
    participant = Participant.objects.get(p_id=participant_id)
    participant.answers = answers  # Store the final answers string
    participant.save()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please enter your quiz code:")
    return QUIZ_CODE

async def quiz_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    logging.info(f"Received quiz code: {code}")
    quiz = await get_quiz_by_code(code)
    if quiz:
        context.user_data['quiz_id'] = quiz.quiz_id
        await update.message.reply_text(f"Quiz found: {quiz.quiz_title}. Now enter your name:")
        return USER_NAME
    else:
        await update.message.reply_text("Invalid quiz code. Please try again:")
        return QUIZ_CODE

async def user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    quiz_id = context.user_data['quiz_id']
    
    participant = await create_participant(name, quiz_id)
    context.user_data['participant_id'] = participant.p_id
    questions = await get_questions(quiz_id)
    
    context.user_data['questions'] = questions
    context.user_data['question_index'] = 0
    context.user_data['answers'] = ""  # Initialize answers string

    if questions:
        await send_question(update, context, questions[0], 0)
        return ANSWER
    else:
        await update.message.reply_text("No questions found for this quiz.")
        return ConversationHandler.END

async def send_question(update, context, question, question_index):
    keyboard = [
        [InlineKeyboardButton(question.option_a, callback_data='A'),
         InlineKeyboardButton(question.option_b, callback_data='B')],
        [InlineKeyboardButton(question.option_c, callback_data='C'),
         InlineKeyboardButton(question.option_d, callback_data='D')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    question_text = f"Question {question_index + 1}: {question.question}"
    logging.info(f"Sending question {question_index + 1}: {question_text}")
    
    if update.callback_query:
        await update.callback_query.message.reply_text(question_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(question_text, reply_markup=reply_markup)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_answer = query.data
    logging.info(f"User selected answer: {selected_answer}")
    
    question_index = context.user_data['question_index']
    questions = context.user_data['questions']
    
    if question_index < len(questions):
        current_question = questions[question_index]
        correct_answer = current_question.ans
        
        # Append '1' for correct or '0' for incorrect to answers string
        context.user_data['answers'] += "1" if selected_answer == correct_answer else "0"
        
        # Move to next question
        question_index += 1
        context.user_data['question_index'] = question_index

        if question_index < len(questions):
            next_question = questions[question_index]
            await send_question(update, context, next_question, question_index)
        else:
            # Save the answers to the Participant model
            answers_string = context.user_data['answers']
            participant_id = context.user_data['participant_id']
            await save_participant_answers(participant_id, answers_string)
            
            # Calculate and display the score
            correct_count = answers_string.count("1")
            total_questions = len(answers_string)
            score_percentage = (correct_count / total_questions) * 100
            score_text = f"Your Score: {correct_count}/{total_questions} ({score_percentage:.2f}%)"
            
            await query.message.reply_text(f"Quiz completed! Thank you for participating.\n\n{score_text}")
            return ConversationHandler.END
    else:
        await query.message.reply_text("No more questions available.")
        return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUIZ_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_code)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_name)],
            ANSWER: [CallbackQueryHandler(answer)]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
