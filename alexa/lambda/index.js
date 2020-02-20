// This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK (v2).
// Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
// session persistence, api calls, and more.
const Alexa = require('ask-sdk-core');
const fetch = require('node-fetch');
const querystring = require('querystring');
const config = require('./config');
const messages = require('./messages');

function htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


const sendProgressiveResponse = (requestEnvelope, message) => {
    const { apiAccessToken, apiEndpoint } = requestEnvelope.context.System;
    const data = {
        "header": {
            "requestId": requestEnvelope.request.requestId,
        },
        "directive": {
            "type": "VoicePlayer.Speak",
            "speech": message,
        }
    };
    fetch(`${apiEndpoint}/v1/directives`, {
        headers: {
            "Authorization": `Bearer ${apiAccessToken}`,
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify(data)
    });
};

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'LaunchRequest';
    },
    async handle(handlerInput) {
        return handlerInput.responseBuilder
            .speak(messages.WELCOME)
            .reprompt(messages.HELP)
            .getResponse();
    }
};

const playAudio = async (audioData, handlerInput) => {
    const stream_url = audioData.stream_url;
    const speechText = `Reproduciendo el capítulo <say-as interpret-as="number">${audioData.episode}</say-as> de la temporada <say-as interpret-as="number">${audioData.season}</say-as> de ${htmlEntities(audioData.title)}`;
    return handlerInput.responseBuilder
        .speak(speechText)
        .withSimpleCard(
            audioData.title,
            `${audioData.episode}x${audioData.season}`
        ).addAudioPlayerPlayDirective('REPLACE_ALL', stream_url, `${audioData.id}:${stream_url}`, 0, undefined, {
            title: audioData.title,
            // subtitle: audioData.description,
            art: new Alexa.ImageHelper().addImageInstance(audioData.image_url).getImage()
        })
        .getResponse();
};

function getSafe(fn) {
    try {
        return fn();
    } catch (e) {
        return undefined;
    }
}

const PlayIntentHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && handlerInput.requestEnvelope.request.intent.name === 'Play';
    },
    async handle(handlerInput) {
        const slots = handlerInput.requestEnvelope.request.intent.slots;
        console.log('Raw slots: ', slots);

        const showId = getSafe(() => slots.Show.resolutions.resolutionsPerAuthority[0].values[0].value.id);
        if (!showId) {
            return handlerInput.responseBuilder
                .speak(`No conozco el programa "${slots.Show.value}", dímelo otra vez`)
                .reprompt(messages.REPROMPT)
                .getResponse();
        }

        sendProgressiveResponse(handlerInput.requestEnvelope, `Buscando ${slots.Show.value}`);

        const slot_params = {
            'show_id': showId,
            'season':
                getSafe(() => slots.Season_Ordinal.resolutions.resolutionsPerAuthority[0].values[0].value.id)
                || slots.Season_Number.value,
            'episode':
                getSafe(() => slots.Episode_Ordinal.resolutions.resolutionsPerAuthority[0].values[0].value.id)
                || slots.Episode_Number.value,
            'station': getSafe(() => slots.Station.value),
        };
        const params = querystring.stringify(slot_params);
        const url = `${config.search_endpoint}?` + params;
        const response = await fetch(url, {
            method: 'get',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            return handlerInput.responseBuilder
                .speak(`<say-as interpret-as="interjection">ehm</say-as>, no he encontrado el episodio de "${slots.Show.value}" que me has pedido, prueba con otro`)
                .reprompt(messages.REPROMPT)
                .getResponse();
        }
        return await playAudio(await response.json(), handlerInput);
    }
};

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && handlerInput.requestEnvelope.request.intent.name === 'AMAZON.HelpIntent';
    },
    handle(handlerInput) {
        return handlerInput.responseBuilder
            .speak(messages.HELP)
            .reprompt(messages.REPROMPT)
            .getResponse();
    }
};

const CancelAndStopIntentHandler = {
    canHandle(handlerInput) {
        const isStopIntent = handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && (handlerInput.requestEnvelope.request.intent.name === 'AMAZON.CancelIntent'
                || handlerInput.requestEnvelope.request.intent.name === 'AMAZON.StopIntent'
                || handlerInput.requestEnvelope.request.intent.name === 'AMAZON.PauseIntent'
                || handlerInput.requestEnvelope.request.intent.name === 'AMAZON.ExitIntent');
        const isPauseCommand = handlerInput.requestEnvelope.request.type === 'PlaybackController.PauseCommandIssued';
        return isStopIntent || isPauseCommand;
    },
    handle(handlerInput) {
        const isPauseIntent = handlerInput.requestEnvelope.request.intent.name === 'AMAZON.PauseIntent';
        const speechText = !isPauseIntent ? messages.GOODBYE : '';
        return handlerInput.responseBuilder
            .speak(speechText)
            .addAudioPlayerStopDirective()
            .getResponse();
    }
};
const ResumeIntentHandler = {
    canHandle(handlerInput) {
        const isResumeIntent = handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && (handlerInput.requestEnvelope.request.intent.name === 'AMAZON.ResumeIntent');
        const isPauseCommand = handlerInput.requestEnvelope.request.type === 'PlaybackController.PlayCommandIssued';
        return isResumeIntent || isPauseCommand;
    },
    handle(handlerInput) {
        const { token, offsetInMilliseconds } = handlerInput.requestEnvelope.context.AudioPlayer;
        const url = token.substring(token.indexOf(':') + 1);
        return handlerInput.responseBuilder
            .addAudioPlayerPlayDirective('REPLACE_ALL', url, token, offsetInMilliseconds)
            .getResponse();
    }
};

const SessionEndedRequestHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'SessionEndedRequest';
    },
    handle(handlerInput) {
        console.log(handlerInput);
        return handlerInput.responseBuilder.getResponse();
    }
};

// The intent reflector is used for interaction model testing and debugging.
// It will simply repeat the intent the user said. You can create custom handlers
// for your intents by defining them above, then also adding them to the request
// handler chain below.
const IntentReflectorHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'IntentRequest';
    },
    handle(handlerInput) {
        const intentName = handlerInput.requestEnvelope.request.intent.name;
        const speechText = `DEBUG ${intentName}`;

        return handlerInput.responseBuilder
            .speak(speechText)
            //.reprompt('add a reprompt if you want to keep the session open for the user to respond')
            .getResponse();
    }
};

const SystemExceptionHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'System.ExceptionEncountered';
    },
    handle(handlerInput) {
        console.log(`System exception encountered`, handlerInput.requestEnvelope.request.error);
    },
};

const NonIntentReflectorHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type !== 'IntentRequest';
    },
    handle(handlerInput) {
        console.log('Unhandled non intent', handlerInput.requestEnvelope.request.type);
        return {};
    }
};

// Generic error handling to capture any syntax or routing errors. If you receive an error
// stating the request handler chain is not found, you have not implemented a handler for
// the intent being invoked or included it in the skill builder below.
const ErrorHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        console.log(`~~~~ Error handled: ${error}`);
        console.log(`~~~~ Error request`, handlerInput.requestEnvelope.request)
        const speechText = messages.ERROR;

        return handlerInput.responseBuilder
            .speak(speechText)
            .getResponse();
    }
};

// This handler acts as the entry point for your skill, routing all request and response
// payloads to the handlers above. Make sure any new handlers or interceptors you've
// defined are included below. The order matters - they're processed top to bottom.
exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(
        SystemExceptionHandler,
        LaunchRequestHandler,
        HelpIntentHandler,
        PlayIntentHandler,
        CancelAndStopIntentHandler,
        ResumeIntentHandler,
        SessionEndedRequestHandler,
        NonIntentReflectorHandler,
        IntentReflectorHandler) // make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    .addErrorHandlers(
        ErrorHandler)
    .lambda();
