const messages = {
  WELCOME: 'Bienvenido a RadioCo. Pregúntame por algún podcast.',
  HELP: 'Puedes decir reproduce seguido del nombre del programa',
  REPROMPT: 'Prueba con: "reproduce spoiler"',
  // SHOW_NOT_FOUND: 'No conozco ningún programa con ese nombre, dímelo otra vez',
  // NOT_FOUND: '<say-as interpret-as="interjection">ehm</say-as>, no he encontrado el episodio que me has pedido, prueba otra vez',
  ERROR: '<say-as interpret-as="interjection">oh no</say-as>, ha ocurrido un error inesperado, inténtalo mas tarde',
  GOODBYE: '<say-as interpret-as="interjection">cuando marchas me entra morriña</say-as>',
  UNHANDLED: 'This skill doesn\'t support that. Please ask something else.',
};

module.exports = messages;