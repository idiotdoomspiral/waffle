import os
import config
import loki
if not config.poop:
    os.chdir('/waffle')

def set_prompt(prompt):
    with open('prompt', 'w+') as prompt_file:
        prompt_file.truncate(0)
        prompt_file.write(str(prompt))
        prompt_file.close()

    loki.log('info', 'puzzle.set_prompt', f'Successfully set prompt to: {prompt}')
def get_prompt():
    with open('prompt') as prompt_file:
        prompt = prompt_file.read()
        prompt_file.close()
    loki.log('info', 'puzzle.get_prompt', f'Sent prompt to user: {prompt}')
    return prompt