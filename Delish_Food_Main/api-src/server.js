const express = require('express');
const mongoose = require('mongoose');
const app = express();
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios')
const path = require('path');
const router = express.Router();
const swaggerJsDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

//required by swagger JS to setup initial swagger doc
const swaggerOptions = {
    swaggerDefinition: {
        openapi: '3.0.0',
        info: {
            version: "1.0.3",
            title: "Delish API",
            description: "Delish API ratings information",
            contact: {
                name: "Cyrus Karsan"
            }
        }
    },
    apis: ["server.js"]
};

//define the OpenAPI doc
const swaggerDocs = swaggerJsDoc(swaggerOptions);

//setup the visual api doc tester
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));
app.options('*',cors());
//cors allows us to access API from different machines with different ips
app.use(cors());
//bodyparser parses json in the request body
app.use(bodyParser.json());



//bodyparser parses json in the request body
app.use(bodyParser.json());

//setup connection to mongoDB atlas
const MongoClient = require('mongodb').MongoClient; //create client to use mongodb
const uri = `mongodb+srv://delishfood:delishfood@cluster0.ailvm.mongodb.net/delishfood?retryWrites=true&w=majority`; //url to connect to mongodb atlas cluster
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true }); //initalize our client

//define MongoDB schema
const RatingSchema = mongoose.Schema({
    placeid: String,
    rating: {
        type: Number,
        default: 0
    }
});

//create a document based on the rating schema
const ratingDoc = mongoose.model('ratingDoc', RatingSchema);

//connect to database
mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true }, () =>
    console.log("Connected to database!"));

/**
 * @swagger
 * /get-docs:
 *  get:
 *    summary: Retrieves all documents in the ratings collection in MongoDB
 *    operationId: get_docs
 *    responses:
 *      '200':
 *        description: Retrieved documents successfully
 *      '500':
 *        description: Unexpected error
 */
router.get('/get-docs', async (req, res) => {
    try {
        const getRatings = await ratingDoc.find();
        res.send(getRatings,200);
    }
    catch (err) {
        res.send({ message: err },500);
    }
});

/**
 * @swagger
 * /add-doc:
 *  post:
 *    summary: Add a new rating to the ratings collection in MongoDB
 *    operationId: add-doc
 *    description: Create a new document in the ratings collection of the resturant and it's rating
 *    requestBody:
 *      required: true
 *      content:
 *          application/json:
 *              schema:
 *                  type: object
 *                  properties:
 *                      placeid:
 *                          type: string
 *                      
 *    responses:
 *      '201':
 *        description: Rating added successfully
 *      '400':
 *        description: Place already in database
 */
router.post('/add-doc', async (req, res) => {
    const rating = new ratingDoc({
        placeid: req.body.placeid,
    });
    let findSpecificDoc = await ratingDoc.find({ placeid: req.body.placeid });
    console.log(findSpecificDoc);
    //make sure we don't add duplicate documents
    if (!findSpecificDoc || findSpecificDoc.length==0) {
        try {
            const savedRating = await rating.save();
            res.send(savedRating,201);
        }
        catch (err) {
            res.json({ message: err });
        }
    }
    else{
        res.status(400).send();
    }
    
});

/**
 * @swagger
 * /{placeid}:
 *  get:
 *    summary: Retrieves document of given id
 *    operationId: retrieve_doc
 *    description: Given a unique google placeid, return the data associated with the document.
 *    parameters:
 *      - name: placeid
 *        in: path 
 *        required: true
 *        description: google placeid
 *        schema:
 *          type: string    
 *    responses:
 *      '200':
 *        description: Place retreived successfully
 *      '404':
 *        description: Place not found 
 */
router.get('/:placeId', async (req, res) => {
    try {
        var findSpecificDoc = await ratingDoc.find({ placeid: req.params.placeId });
        console.log(findSpecificDoc)
    }
    catch (err) {
        res.json({ message: err });
    }

    //couldn't find document
    if (!findSpecificDoc || findSpecificDoc.length==0) {
        res.status(404).send();
    }
    //doc found, return its rating
    else {
        rating = findSpecificDoc[0].rating;
        //res.send({"rating":rating});
        res.send(findSpecificDoc)
    }
});

/**
 * @swagger
 * /{placeid}:
 *  delete:
 *    summary: Removes document from ratings collection
 *    operationId: delete_doc
 *    description: Given a unique google placeid, delete the document associated with the id
 *    parameters:
 *      - name: placeid
 *        in: path 
 *        required: true
 *        description: unique google placeid
 *        schema:
 *          type: string
 *    responses:
 *      '200':
 *        description: Place deleted successfully
 *      '404':
 *        description: Place not found 
 */
router.delete('/:placeId', async (req, res) => {
    try {
        var mongoRemovedMsg = await ratingDoc.remove({ placeid: req.params.placeId });
    }
    catch (err) {
        res.json({ message: err });
    }
    if (mongoRemovedMsg.deletedCount == 1) {
        res.send({"Deleted": true},200)
    }
    else {
        res.send(404);
    }
});
/**
 * @swagger
 * /upvote:
 *  put:
 *    summary: Increment resturant rating by 1
 *    operationId: upvote
 *    description: Given a placeid, update its rating by 1
 *    requestBody:
 *      required: true
 *      content:
 *          application/json:
 *              schema:
 *                  type: object
 *                  properties:
 *                      placeid:
 *                          type: string
 *                      
 *    responses:
 *      '200':
 *        description: Rating incremented by 1
 *      '400':
 *        description: place not found
 */
router.put('/upvote', async (req, res) => {
    try {
        var updatedDocMsg = await ratingDoc.updateOne({ placeid: req.body.placeid }, { $inc: { rating: 1 } });
    }
    catch (err) {
        res.json({ message: err });
    }
    if (updatedDocMsg.n==1) {
        res.send(200)
    }
    else{
        res.send(404)
    }
});

/**
 * @swagger
 * /downvote:
 *  put:
 *    summary: Decrement resturant rating by 1
 *    operationId: downvote
 *    description: Given a placeid, decrement its rating by 1
 *    requestBody:
 *      required: true
 *      content:
 *          application/json:
 *              schema:
 *                  type: object
 *                  properties:
 *                      placeid:
 *                          type: string
 *                      
 *    responses:
 *      '200':
 *        description: Rating decremented by 1
 *      '400':
 *        description: Place not found
 */
router.put('/downvote', async (req, res) => {
    try {
        var updatedDocMsg = await ratingDoc.updateOne({ placeid: req.body.placeid }, { $inc: { rating: -1 } });
    }
    catch (err) {
        res.json({ message: err });
    }
    if (updatedDocMsg.n==1) {
        res.send(200)
    }
    else {
        res.send(404)
    }
});

app.use('/', router);
app.listen(process.env.port || 8080);

console.log('Server listening on port 8080!');
console.log('Open up a browser and go to localhost:8080/');
