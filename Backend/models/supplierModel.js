const mongoose = require('mongoose');

const supplierSchema = new mongoose.Schema({
  name: { type: String },
  level: { type: Number },
  link: { type: String },
  country: { type: String },
  rating: { type: String },
  prevOrders: { type: String },
  experience: { type: String },
});

module.exports = mongoose.model('Supplier', supplierSchema);
