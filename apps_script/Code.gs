// Replace with your ngrok HTTPS URL each time you restart ngrok.
const CHECKIN_URL = 'https://buzz-visor-bluish.ngrok-free.dev/checkin';

// Question title constants -- must match your Google Form question text exactly.
const Q_FIRST_NAME = 'First Name';
const Q_LAST_NAME  = 'Last Name';
const Q_EMAIL      = 'Email';
const Q_BADGE_ID   = 'Badge ID';

function onFormSubmit(e) {
  var itemResponses = e.response.getItemResponses();

  var values = {};
  for (var i = 0; i < itemResponses.length; i++) {
    values[itemResponses[i].getItem().getTitle()] = itemResponses[i].getResponse();
  }

  var payload = {
    first_name: values[Q_FIRST_NAME],
    last_name:  values[Q_LAST_NAME],
    email:      values[Q_EMAIL],
    badge_id:   values[Q_BADGE_ID]
  };

  var options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  var response = UrlFetchApp.fetch(CHECKIN_URL, options);
  Logger.log('Status: ' + response.getResponseCode());
  Logger.log('Body: '   + response.getContentText());
}

function testOnFormSubmit() {
  var mockEvent = {
    response: {
      getItemResponses: function() {
        return [
          { getItem: function() { return { getTitle: function() { return 'First Name'; } }; }, getResponse: function() { return 'Jane'; } },
          { getItem: function() { return { getTitle: function() { return 'Last Name'; } }; },  getResponse: function() { return 'Doe'; } },
          { getItem: function() { return { getTitle: function() { return 'Email'; } }; },       getResponse: function() { return 'jane@example.com'; } },
          { getItem: function() { return { getTitle: function() { return 'Badge ID'; } }; },   getResponse: function() { return 'B-001'; } }
        ];
      }
    }
  };
  onFormSubmit(mockEvent);
}
