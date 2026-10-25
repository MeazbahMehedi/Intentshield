"""Local administration and reproducible experiment CLI."""
import argparse
import getpass
import json
from pathlib import Path
from werkzeug.security import generate_password_hash
from intentshield import create_app
from intentshield.database.db import db
from intentshield.services.evaluation import evaluate, dataset_audit


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='command',required=True)
    user=sub.add_parser('user');user.add_argument('name');user.add_argument('--role',choices=['admin','analyst'],default='analyst')
    sub.add_parser('audit-datasets')
    ev=sub.add_parser('evaluate');ev.add_argument('--split',default='holdout',choices=['development','holdout','robustness','test']);ev.add_argument('--mode',default='hybrid',choices=['rules','hybrid','ml']);ev.add_argument('--output');ev.add_argument('--include-overlaps',action='store_true')
    args=parser.parse_args()
    app=create_app()
    with app.app_context():
        if args.command=='user':
            if not args.name or len(args.name)>80:parser.error('Username must be 1–80 characters.')
            password=getpass.getpass('Password (minimum 12 characters): ')
            if len(password)<12:parser.error('Password is too short.')
            if password!=getpass.getpass('Confirm password: '):parser.error('Passwords do not match.')
            # Existing accounts require a separate intentional removal, preventing accidental overwrite.
            if db().execute('SELECT name FROM users WHERE name=?',(args.name,)).fetchone():parser.error('User already exists.')
            db().execute('INSERT INTO users VALUES (?,?,?)',(args.name,generate_password_hash(password),args.role));db().commit();print('User created.')
        else:
            result=dataset_audit() if args.command=='audit-datasets' else evaluate(args.split,args.mode,not args.include_overlaps)
            text=json.dumps(result,indent=2)
            if getattr(args,'output',None):Path(args.output).write_text(text,encoding='utf-8')
            else:print(text)

if __name__=='__main__':main()
