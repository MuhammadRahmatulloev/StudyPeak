document.addEventListener('DOMContentLoaded', function () {
    var meta = document.getElementById('quizMeta');
    if (!meta) return;

    var totalSeconds = parseInt(meta.getAttribute('data-time')) || 0;
    var totalQuestions = parseInt(meta.getAttribute('data-total')) || 0;
    var hasTimer = meta.getAttribute('data-has-timer') === '1';

    var form = document.getElementById('quizForm');
    var submitBtn = document.getElementById('submitQuizBtn');
    var timerDisplay = document.getElementById('timerDisplay');
    var timerFinal = document.getElementById('timerFinal');
    var timerEl = document.getElementById('quizTimer');
    var answeredCountEl = document.getElementById('answeredCount');
    var answeredFinalEl = document.getElementById('answeredFinal');

    var isSubmitting = false;

    function formatTime(seconds) {
        var m = Math.floor(seconds / 60).toString().padStart(2, '0');
        var s = (seconds % 60).toString().padStart(2, '0');
        return m + ':' + s;
    }

    function submitForm() {
        if (isSubmitting) return;
        isSubmitting = true;
        window.removeEventListener('beforeunload', onBeforeUnload);
        form.submit();
    }

    if (hasTimer && totalSeconds > 0) {
        var countdown = setInterval(function () {
            totalSeconds--;

            if (totalSeconds <= 0) {
                clearInterval(countdown);
                submitForm();
                return;
            }

            var formatted = formatTime(totalSeconds);
            if (timerDisplay) timerDisplay.textContent = formatted;
            if (timerFinal) timerFinal.textContent = formatted;

            if (timerEl) {
                if (totalSeconds <= 60) {
                    timerEl.classList.remove('timer-warning');
                    timerEl.classList.add('timer-danger');
                } else if (totalSeconds <= 180) {
                    timerEl.classList.add('timer-warning');
                }
            }
        }, 1000);
    }

    document.querySelectorAll('.quiz-choice-radio').forEach(function (radio) {
        radio.addEventListener('change', function () {
            var name = this.name;
            document.querySelectorAll('input[name="' + name + '"]').forEach(function (r) {
                var parent = r.closest('.quiz-choice, .quiz-tf-btn');
                if (parent) parent.classList.remove('selected');
            });
            var parent = this.closest('.quiz-choice, .quiz-tf-btn');
            if (parent) parent.classList.add('selected');
            updateProgress();
        });
    });

    document.querySelectorAll('.quiz-textarea').forEach(function (ta) {
        ta.addEventListener('input', updateProgress);
    });

    document.querySelectorAll('.quiz-nav-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var num = this.getAttribute('data-num');
            var el = document.getElementById('question-' + num);
            if (!el) return;
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.classList.add('question-highlight');
            setTimeout(function () {
                el.classList.remove('question-highlight');
            }, 1000);
        });
    });

    function updateProgress() {
        var answered = 0;

        document.querySelectorAll('.quiz-question-card').forEach(function (card, idx) {
            var num = idx + 1;
            var navBtn = document.getElementById('nav-btn-' + num);
            var textArea = card.querySelector('textarea');
            var radioChecked = card.querySelector('input[type="radio"]:checked');
            var isAnswered = false;

            if (textArea) {
                isAnswered = textArea.value.trim().length > 0;
            } else if (radioChecked) {
                isAnswered = true;
            }

            if (isAnswered) {
                answered++;
                if (navBtn) navBtn.classList.add('nav-btn-answered');
            } else {
                if (navBtn) navBtn.classList.remove('nav-btn-answered');
            }
        });

        if (answeredCountEl) answeredCountEl.textContent = answered;
        if (answeredFinalEl) answeredFinalEl.textContent = answered;
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', function () {
            var answeredCount = parseInt((answeredFinalEl && answeredFinalEl.textContent) || '0');
            var unanswered = totalQuestions - answeredCount;
            var msg = unanswered > 0
                ? 'You have ' + unanswered + ' unanswered question(s). Submit anyway?'
                : 'Submit quiz? You cannot change answers after this.';
            if (window.confirm(msg)) {
                submitForm();
            }
        });
    }

    function onBeforeUnload(e) {
        if (isSubmitting) return;
        e.preventDefault();
        e.returnValue = '';
    }

    window.addEventListener('beforeunload', onBeforeUnload);

    updateProgress();
});