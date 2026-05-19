"""Management command to seed the database with realistic sample data.

Usage:
    python manage.py seed_database
    python manage.py seed_database --flush         # wipe existing data first
    python manage.py seed_database --users 15 --boards 6
"""

from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from board_app.models import Board
from tasks_app.models import Task, TaskComment


GUEST_USERNAME = 'Gast Account'
GUEST_EMAIL = 'gast@demo.de'

SAMPLE_USERS = [
    ('Alice', 'Schneider'),
    ('Bob', 'Müller'),
    ('Carol', 'Becker'),
    ('David', 'Fischer'),
    ('Eva', 'Wagner'),
    ('Frank', 'Hoffmann'),
    ('Greta', 'Schulz'),
    ('Hans', 'Weber'),
    ('Isa', 'Krüger'),
    ('Jonas', 'Lehmann'),
    ('Karla', 'Zimmermann'),
    ('Lars', 'Braun'),
]

BOARD_TITLES = [
    'Produkt-Roadmap 2026',
    'Marketing Q2',
    'Backend-Refactoring',
    'Mobile App Release',
    'Onboarding-Prozess',
    'Bugfix-Sprint',
    'Design-System',
    'Kundenfeedback',
]

TASK_TEMPLATES = [
    ('Login-Flow überarbeiten', 'OAuth2-Integration und Passwort-Reset implementieren.'),
    ('REST-API dokumentieren', 'OpenAPI-Spezifikation für alle Endpunkte erstellen.'),
    ('Dashboard-UI bauen', 'Übersichtsseite mit Statistik-Widgets entwickeln.'),
    ('Performance optimieren', 'Datenbankabfragen profilen und Indizes setzen.'),
    ('E-Mail-Benachrichtigungen', 'Versand bei Task-Zuweisung und Kommentaren.'),
    ('Drag & Drop für Tasks', 'Spalten-übergreifendes Verschieben per Maus.'),
    ('CI/CD-Pipeline einrichten', 'Automatisierte Tests und Deployments via GitHub Actions.'),
    ('Sicherheitsaudit', 'OWASP Top 10 prüfen und Schwachstellen schließen.'),
    ('Mobile Ansicht testen', 'Responsives Layout auf iOS und Android verifizieren.'),
    ('Benutzerrollen einführen', 'Admin-, Editor- und Viewer-Rollen umsetzen.'),
    ('Filter & Suche', 'Volltextsuche über Tasks und Kommentare.'),
    ('Dark Mode', 'Theming-System und Farbpalette für dunklen Modus.'),
    ('Onboarding-Guide', 'Interaktive Tour für Neunutzer erstellen.'),
    ('Bug: Doppelklick speichert zweimal', 'Race Condition im Save-Handler beheben.'),
    ('Reporting-Export', 'CSV- und PDF-Export von Boards bereitstellen.'),
    ('Push-Benachrichtigungen', 'WebPush-API für Browser-Notifications einbinden.'),
]

COMMENT_SNIPPETS = [
    'Sieht gut aus, ich übernehme das Review.',
    'Habe noch Rückfragen zur Spezifikation.',
    'Bitte Deadline im Auge behalten.',
    'Erste Version ist deployed, bitte testen.',
    'Blocker: warte auf Feedback vom Design-Team.',
    'Tests laufen grün, von mir ein +1.',
    'Ich würde das Ticket gerne splitten.',
    'Status auf "Review" gesetzt.',
    'Könnten wir das in der nächsten Iteration angehen?',
    'Dokumentation wurde aktualisiert.',
]

STATUS_VALUES = ['to-do', 'in_progress', 'review', 'done']
PRIORITY_VALUES = ['low', 'medium', 'high']

DEFAULT_PASSWORD = 'password123'


class Command(BaseCommand):
    """Populate the database with realistic demo data."""

    help = 'Seed the database with users, boards, tasks and comments.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing boards, tasks, comments and demo users first.',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of demo users to create (max %d).' % len(SAMPLE_USERS),
        )
        parser.add_argument(
            '--boards',
            type=int,
            default=5,
            help='Number of boards to create (max %d).' % len(BOARD_TITLES),
        )
        parser.add_argument(
            '--seed',
            type=int,
            default=42,
            help='Random seed for reproducible data.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options['seed'])

        if options['flush']:
            self._flush()

        users = self._create_users(options['users'])
        boards = self._create_boards(users, options['boards'])
        tasks = self._create_tasks(boards)
        self._create_comments(tasks, users)

        self.stdout.write(self.style.SUCCESS(
            f'Seed erfolgreich: {len(users)} Nutzer, {len(boards)} Boards, '
            f'{len(tasks)} Tasks erstellt.'
        ))
        self.stdout.write(self.style.WARNING(
            f'Demo-Login: {GUEST_EMAIL} / {DEFAULT_PASSWORD} (Username: "{GUEST_USERNAME}")'
        ))

    def _flush(self):
        self.stdout.write('Lösche bestehende Demo-Daten...')
        TaskComment.objects.all().delete()
        Task.objects.all().delete()
        Board.objects.all().delete()
        usernames = [f'{first} {last}' for first, last in SAMPLE_USERS] + [GUEST_USERNAME]
        User.objects.filter(username__in=usernames).delete()

    def _create_users(self, count):
        guest, created = User.objects.get_or_create(
            username=GUEST_USERNAME,
            defaults={'email': GUEST_EMAIL, 'first_name': 'Gast', 'last_name': 'Account'},
        )
        if created or guest.email != GUEST_EMAIL:
            guest.email = GUEST_EMAIL
            guest.set_password(DEFAULT_PASSWORD)
            guest.save()

        count = max(1, min(count, len(SAMPLE_USERS)))
        users = []
        for first, last in SAMPLE_USERS[:count]:
            username = f'{first} {last}'
            email = f'{first}.{last}@example.com'.lower()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                },
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
            users.append(user)
        users.append(guest)
        return users

    def _create_boards(self, users, count):
        count = max(1, min(count, len(BOARD_TITLES)))
        guest = User.objects.get(username=GUEST_USERNAME)
        non_guest_users = [u for u in users if u != guest]
        boards = []
        for index, title in enumerate(BOARD_TITLES[:count]):
            # Guest is owner of the first board, member of all others -
            # so the demo account always sees every board.
            owner = guest if index == 0 else random.choice(non_guest_users)
            board, _ = Board.objects.get_or_create(
                title=title,
                defaults={'owner': owner},
            )
            member_pool = [u for u in non_guest_users if u != board.owner]
            sample_size = min(len(member_pool), random.randint(2, 5))
            members = random.sample(member_pool, sample_size)
            board.members.set([board.owner, guest, *members])
            boards.append(board)
        return boards

    def _create_tasks(self, boards):
        tasks = []
        today = timezone.now().date()
        for board in boards:
            members = list(board.members.all())
            if not members:
                continue
            task_count = random.randint(4, 8)
            templates = random.sample(
                TASK_TEMPLATES,
                k=min(task_count, len(TASK_TEMPLATES)),
            )
            for title, description in templates:
                assignee = random.choice(members)
                reviewer_pool = [m for m in members if m != assignee] or [assignee]
                reviewer = random.choice(reviewer_pool)
                task = Task.objects.create(
                    board=board,
                    title=title,
                    description=description,
                    status=random.choice(STATUS_VALUES),
                    priority=random.choice(PRIORITY_VALUES),
                    assignee=assignee,
                    reviewer=reviewer,
                    due_date=today + timedelta(days=random.randint(-5, 30)),
                )
                tasks.append(task)
        return tasks

    def _create_comments(self, tasks, users):
        for task in tasks:
            comment_count = random.randint(0, 4)
            if not comment_count:
                continue
            candidates = list({task.assignee, task.reviewer, *random.sample(users, 3)})
            candidates = [u for u in candidates if u is not None]
            for _ in range(comment_count):
                author = random.choice(candidates)
                TaskComment.objects.create(
                    task=task,
                    author=author,
                    content=random.choice(COMMENT_SNIPPETS),
                )
            task.comments_count = comment_count
            task.save(update_fields=['comments_count'])
