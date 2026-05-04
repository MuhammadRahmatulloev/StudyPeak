from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
import json
import requests
from datetime import date
from accounts.permissions import SessionLoginRequiredMixin, get_current_user
from .models import AIRequest, AIUsageLimit


BLOCKED_KEYWORDS = [
    'сделай дз', 'напиши код', 'реши задачу', 'напиши ответ',
    'сделай за меня', 'реши пример', 'напиши решение',
    'do my homework', 'write code', 'solve this', 'give me the answer',
    'write the answer', 'complete my assignment',
]

DAILY_LIMIT = 20

SYSTEM_PROMPT = """You are StudyPeak AI — an educational assistant.
Your role is to help students understand topics and concepts clearly and simply.

Rules:
- Explain topics in a simple and clear way
- Help students understand concepts
- Do NOT write full homework answers
- Do NOT write code solutions for programming tasks
- Do NOT solve math homework directly — explain the method instead
- If a student asks you to do their homework, respond:
  "I can't complete the task for you, but I can explain the topic so you can do it yourself."

Always respond in the same language the student uses."""


def is_cheating(question):
    q = question.lower()
    return any(keyword in q for keyword in BLOCKED_KEYWORDS)


def reset_limit_if_needed(limit):
    today = date.today()
    if limit.last_reset_date != today:
        limit.daily_count = 0
        limit.last_reset_date = today
        limit.save()


def ask_groq(prompt, system_prompt, api_key):
    if not api_key:
        return None
    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': 1024,
            },
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        if response.status_code == 429:
            return None
    except Exception:
        pass
    return None


def get_ai_response(prompt, system_prompt):
    keys = [
        settings.GROQ_API_KEY1,
        settings.GROQ_API_KEY2,
        settings.GROQ_API_KEY3,
    ]
    for key in keys:
        result = ask_groq(prompt, system_prompt, key)
        if result:
            return result
    return None


class AIRequestView(SessionLoginRequiredMixin, View):
    def post(self, request):
        user = get_current_user(request)

        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid request.'}, status=400)

        question = data.get('question', '').strip()
        context = data.get('context', AIRequest.GENERAL)
        lesson_id = data.get('lesson_id') or None
        assignment_id = data.get('assignment_id') or None

        if not question:
            return JsonResponse({'error': 'Question is required.'}, status=400)

        limit, _ = AIUsageLimit.objects.get_or_create(user=user)
        reset_limit_if_needed(limit)

        if limit.daily_count >= DAILY_LIMIT:
            return JsonResponse({
                'error': f'Daily limit of {DAILY_LIMIT} questions reached. Try again tomorrow.'
            }, status=429)

        if is_cheating(question):
            AIRequest.objects.create(
                user=user,
                question=question,
                response="I can't complete the task for you, but I can explain the topic so you can do it yourself.",
                context=context,
                is_blocked=True,
            )
            return JsonResponse({
                'response': "I can't complete the task for you, but I can explain the topic so you can do it yourself.",
                'blocked': True,
            })

        lesson = None
        assignment = None

        if lesson_id:
            from materials.models import Lesson
            lesson = Lesson.objects.filter(id=lesson_id).first()

        if assignment_id:
            from assignments.models import Assignment
            assignment = Assignment.objects.filter(id=assignment_id).first()

        context_info = ''
        if lesson:
            context_info = f'\n\nContext: The student is studying lesson "{lesson.title}" from subject "{lesson.subject.title}".'
        elif assignment:
            context_info = f'\n\nContext: The student is working on assignment "{assignment.title}" (type: {assignment.type}).'

        full_system = SYSTEM_PROMPT + context_info
        response_text = get_ai_response(question, full_system)

        if not response_text:
            response_text = 'Sorry, the AI assistant is temporarily unavailable. Please try again later.'

        AIRequest.objects.create(
            user=user,
            question=question,
            response=response_text,
            context=context,
            lesson=lesson,
            assignment=assignment,
            is_blocked=False,
        )

        limit.daily_count += 1
        limit.save()

        return JsonResponse({
            'response': response_text,
            'blocked': False,
            'requests_left': DAILY_LIMIT - limit.daily_count,
        })


class AIHistoryView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)

        if user.is_admin_role:
            history = AIRequest.objects.select_related('user', 'lesson', 'assignment').all()
        else:
            history = AIRequest.objects.filter(user=user).select_related('lesson', 'assignment')

        return render(request, 'ai/history.html', {'history': history})


class AIHistoryDeleteView(SessionLoginRequiredMixin, View):
    def post(self, request, request_id):
        user = get_current_user(request)
        ai_request = get_object_or_404(AIRequest, id=request_id)

        if ai_request.user != user and not user.is_admin_role:
            messages.error(request, 'Access denied.')
            return redirect('ai_history')

        ai_request.delete()
        messages.success(request, 'Request deleted.')
        return redirect('ai_history')


class AIUsageLimitListView(SessionLoginRequiredMixin, View):
    def get(self, request):
        user = get_current_user(request)
        if not user.is_admin_role:
            messages.error(request, 'Admin access required.')
            return redirect('home')

        limits = AIUsageLimit.objects.select_related('user').all().order_by('-daily_count')
        return render(request, 'ai/usage_limits.html', {'limits': limits})