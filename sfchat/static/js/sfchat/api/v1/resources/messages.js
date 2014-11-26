/**
 * sfchat/api/v1/resources/message.js: SFChat Api Message Resource
 */

"use strict";

// check namespace
var SFChat;
if (!SFChat.api || !SFChat.api.client) {
    throw new Error('One of required modules was not loaded.');
} else if (!SFChat.api.resources) {
    SFChat.api.resources = {};
}
    
if (SFChat.api.resources.messages) {
    throw new Error('Module with name SFChat.api.resources.messages has already exist.');
}

/**
 * SFChat Message Resource
 * 
 * @type {Function}
 * @param {SFChat.api.client} client
 */
SFChat.api.resources.messages = function(client) {
    this.client = {};
    this._name  = 'messages';
    this._setClient(client);
};

/**
 * Post message
 * 
 * @param {String} msg
 * @param {Object} callback
 * @param {Function} callback.method
 * @param {Object} callback.obj
 * @throws {Error}
 */
SFChat.api.resources.messages.prototype.postMessage = function(msg, callback) {
    var _this = this,
        data;
  
    if (_this._validateMessage(msg) === true) {
        data = _this._prepareMessageForSend(msg);
        this.client.sendRequest('POST', _this._name, data, callback);
    } else {
        throw new Error('Message has invalid format.');
    }
};

/**
 * Gets message
 * 
 * @param {Function} callback.method
 * @param {Object} callback.obj
 */
SFChat.api.resources.messages.prototype.getMessage = function(callback) {
    var _this = this;
    
    this.client.sendRequest('GET', _this._name, undefined, callback);
};

/**
 * Delete message
 * 
 * @param {Object} data
 * @param {Object} data.messages
 * @param {Array} data.messages
 * @param {Object} data.messages[0]
 * @param {String} data.messages[0]._id
 * @param {Function} callback.method
 * @param {Object} callback.obj
 */
SFChat.api.resources.messages.prototype.deleteMessage = function(data, callback) {
    var _this = this;
    
    this.client.sendRequest('DELETE', _this._name, data, callback);
};

/**
 * Sets Api Client
 * 
 * @param {SFChat.api.client} client
 */
SFChat.api.resources.messages.prototype._setClient = function(client) {
    if (typeof(client) !== 'object' 
        || typeof(client.sendRequest) !== 'function'
    ) {
        throw new TypeError('Client is not valid API Client.');
    }
    
    this.client = client;
};

/**
 * Validate message
 * 
 * @param {String} msg
 * @return {Boolean} true if ok or false otherwise
 */
SFChat.api.resources.messages.prototype._validateMessage = function(msg) {
    var msg_length = msg.length;
    
    return msg_length !== 0 && msg_length <= 144;
};

/**
 * Prepare message for send
 * 
 * @param {String} msg
 * @return {Object}
 */
SFChat.api.resources.messages.prototype._prepareMessageForSend = function(msg) {
    return {
        data: {messages: [{msg: msg}]}
    };
};