from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from tom_targets.models import Target
from guardian.shortcuts import assign_perm


class Command(BaseCommand):
    help = 'Assign permissions for targets to users or groups'

    def add_arguments(self, parser):
        parser.add_argument('target_name', type=int, help='ID of the target to assign permissions to')
        parser.add_argument('--user', nargs='+', type=str, help='Username(s) to assign permissions to')
        parser.add_argument('--group', nargs='+', type=str, help='Group(s) to assign permissions to')

    def handle(self, *args, **options):
        target_name = options['target_name']
        users = options['user']
        groups = options['group']

        target = Target.objects.get(name=target_name)
        # permissions = ['view_target', 'change_target', 'delete_target']
        permissions = ['view_target']

        for permission in permissions:
            # Assign permissions to users
            if users:
                for username in users:
                    user = User.objects.get(username=username)
                    assign_perm(f'targets.{permission}', user, target)
                    self.stdout.write(self.style.SUCCESS(f"Permission '{permission}' assigned to user '{username}' for target '{target.name}'"))

            # Assign permissions to groups
            if groups:
                for group_name in groups:
                    group = Group.objects.get(name=group_name)
                    assign_perm(f'targets.{permission}', group, target)
                    self.stdout.write(self.style.SUCCESS(f"Permission '{permission}' assigned to group '{group_name}' for target '{target.name}'"))
