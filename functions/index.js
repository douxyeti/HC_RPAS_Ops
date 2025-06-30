// Import the necessary modules.
const functions = require("firebase-functions");
const admin = require("firebase-admin");

// Initialize the Firebase Admin SDK.
// The SDK will automatically use the project's service account credentials
// when deployed to the Firebase/Google Cloud environment.
admin.initializeApp();

/**
 * Cloud Function to generate a Single Sign-On (SSO) custom token.
 * This function is callable directly from the client application.
 *
 * @param {object} data - The data passed from the client.
 * @param {string} data.idToken - The Firebase ID token of the authenticated user.
 * @param {functions.https.CallableContext} context - The context of the function call.
 *
 * @returns {Promise<{customToken: string}|{error: string}>} - A promise that resolves with
 * an object containing the custom token, or an error object.
 */
// Import the cors module to handle cross-origin requests
const cors = require("cors")({origin: true});

exports.generateSsoToken = functions.https.onRequest((req, res) => {
  // Utiliser le middleware CORS pour gérer les en-têtes
  cors(req, res, async () => {
    // Logguer le corps de la requête pour le débogage
    functions.logger.info("SSO Function: Requête reçue. Corps:", req.body);

    // Vérifier que la méthode de la requête est POST
    if (req.method !== 'POST') {
      return res.status(405).send('Method Not Allowed');
    }

    // The client sends the idToken directly in the body.
    const idToken = req.body.idToken;

    if (!idToken) {
      const errorMessage = "ID token is missing from the request body.";
      functions.logger.error(`SSO Token Generation: ${errorMessage}`);
      return res.status(400).send({ error: errorMessage });
    }

    try {
      // 3. Verify the ID token.
      const decodedToken = await admin.auth().verifyIdToken(idToken);
      const uid = decodedToken.uid;
      functions.logger.info(`Verified ID token for UID: ${uid}. Generating custom token.`);

      // 4. Create a custom token for the verified user.
      const customToken = await admin.auth().createCustomToken(uid);
      functions.logger.info(`Successfully generated custom token for UID: ${uid}.`);

      // 5. Return the custom token to the client.
      return res.status(200).send({ customToken: customToken });

    } catch (error) {
      functions.logger.error("Error generating SSO token:", error);
      return res.status(500).send({ error: "An unexpected error occurred while generating the SSO token." });
    }
  });
});
