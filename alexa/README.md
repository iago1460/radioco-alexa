# Alexa skill

This folder contains helpers and Alexa code needed to deploy the skill. 

## Dependencies

You will need to install [npm](https://www.npmjs.com/) and [invoke](http://www.pyinvoke.org/).

run `npm install && npm run ask -- init` before running the below. 
Enter the username and password for the account that has access to https://developer.amazon.com/.
When asked you can skip the AWS credential steps as that is not necessary

TROUBLESHOOTING:
If you get no response from the cli try closing and reopening the terminal run `npm run ask -- api list-skills` to see if you get any response


## Usage

### Commands

Download interaction models from Amazon:

    inv get-models
    inv get-model radioco

Upload interaction models to Amazon from json files: 

    inv upload-models
    inv upload-model radioco

Validate a skill

    inv validate radioco


### Helpers

To update interaction model with the latest shows, run:

    python3 update_interaction_models.py

Keep in mind the command will override existing synonyms and 
other changes that are not in the template.json
