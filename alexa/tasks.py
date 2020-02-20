import zipfile
import os
import pathlib
import tempfile
from invoke import task
import pip
import invoke

os.environ['ASK_DEFAULT_PROFILE'] = 'radioco'

EXCLUDED_FILES = ['pyc']

APP_ID_BY_SKILL = {
    'radioco': 'amzn1.ask.skill.06c61e46-a81f-4ef9-905e-25db22db2146',
    'cuacfm': 'amzn1.ask.skill.172358b5-6394-468c-840f-aeae5937f4f5',
}


def add_directory(zipfile, path, dest):
    for root, dirs, files in os.walk(path, followlinks=True):
        for f in files:
            for file_extension in EXCLUDED_FILES:
                if not f.endswith(file_extension):
                    rel_path = os.path.relpath(root, path)
                    zipfile.write(os.path.join(root, f), os.path.join(dest, rel_path, f))


def add_requirements(zipfile, requirements_path, prefix='alexa-'):
    # AWS Lambda requires dependencies to be included alongside the skill code.
    # Note that any packages with C modules will need compiling specifically for AWS Lambda.
    target_path = tempfile.mkdtemp(prefix=prefix)
    pip.main(['install', '-r', requirements_path, '-t', target_path, '--ignore-installed'])
    add_directory(zipfile, target_path, '/')


@task
def package(ctx, skill):
    print('Packaging lambda zip')
    pathlib.Path('./deploy').mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(f'deploy/{skill}.zip', 'w') as deploy:
        add_directory(deploy, 'lambda', 'alexa')
        add_directory(deploy, f'./{skill}/{skill}', f'./{skill}')
        add_requirements(deploy, f'./{skill}/requirements.txt', prefix=f'alexa-{skill}')


@task
def deploy(ctx, skill):
    try:
        lambda_function = ctx['skills'][skill]['aws_lambda_arn']
    except KeyError:
        raise invoke.Exit(f'Invalid skill: "{skill}"')
    package(ctx, skill)
    print('Deploying "{}" skill to: {}'.format(skill, lambda_function))
    ctx.run(f'aws lambda update-function-code --function-name {lambda_function} --zip-file fileb:///alexa/deploy/{skill}.zip --publish')


@task
def get_models(ctx):
    for skill in APP_ID_BY_SKILL.keys():
        get_model(ctx, skill)


@task
def upload_models(ctx):
    for skill in APP_ID_BY_SKILL.keys():
        upload_model(ctx, skill)


@task
def get_model(ctx, skill):
    app_id = APP_ID_BY_SKILL.get(skill)
    if app_id:
        file_path = f'./interaction_models/{skill}.json'
        print(f'Saving {skill} interaction model to {file_path}')
        ctx.run(f'npm run ask -s -- api get-model -s {app_id} -l es-ES > {file_path}')


@task
def upload_model(ctx, skill):
    app_id = APP_ID_BY_SKILL.get(skill)
    if app_id:
        file_path = f'./interaction_models/{skill}.json'
        print(f'Uploading {skill} interaction model to es-ES from {file_path}')
        ctx.run(f'npm run ask -- api update-model -s {app_id} -l es-ES -f {file_path}')


@task
def validate(ctx, skill):
    app_id = APP_ID_BY_SKILL.get(skill)
    if app_id:
        ctx.run(f'npm run ask -- validate -s {app_id} -l es-ES')


@task
def list_skills(ctx):
    ctx.run('npm run ask -- api list-skills')
