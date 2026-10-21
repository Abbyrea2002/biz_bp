from bson import ObjectId
from decorators import jwt_required, admin_required
from flask import Blueprint, request, make_response, jsonify
import globals

reviews_bp = Blueprint("reviews_bp", __name__)

businesses = globals.db.biz

@reviews_bp.route("/api/v1.0/businesses/<string:id>/reviews", methods=["POST"])
@jwt_required
def add_new_review(id):
 if "username" in request.form and "comment" in request.form and "stars" in request.form:

    new_review = {
        "_id" : ObjectId(),
        "username" : request.form["username"],
        "comment" : request.form["comment"],
        "stars" : request.form["stars"]
    }
    result = businesses.update_one({"_id" : ObjectId(id)}, \
                                   {"$push" : {"reviews" : new_review}})
    if result.matched_count == 1:
        new_review_link = \
        "http://localhost:5000/api/v1.0/businesses/" \
        + id +"reviews/" + str(new_review["_id"])
        return make_response(jsonify({"url": new_review_link}), 201)
    else:
        return make_response(jsonify({"error" : "Invalid business ID"}), 404)
 else:
    return make_response(jsonify({"error" : "Missing form data"}), 404)

@reviews_bp.route("/api/v1.0/businesses/<string:id>/reviews", methods=["GET"])
def fetch_all_reviews(id):
 if re.fullmatch(r"[0-9a-fA-F]{24}", id):
     data_to_return = []
     business = businesses.find_one( 
                                   {"_id" : ObjectId(id)},
                                   {"reviews" : 1, "_id" : 0})
     if business is None:
        return make_response(jsonify({"error" : "Invalid business ID"}), 404)
     for review in business["reviews"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)
     return make_response(jsonify(data_to_return), 200)
 else:
  return make_response(jsonify({"error" : "Invalid ID"}), 404)

@reviews_bp.route("/api/v1.0/businesses/<bid>/reviews/<rid>", methods=["GET"])
def fetch_one_review(bid,rid):
    business = businesses.find_one(
        {"_id": ObjectId(bid)},
        {"reviews" : 1})
    if business is None:
        return make_response(jsonify({"error" : "Invalid business ID"}), 404)

    review_id = ObjectId(rid)
    review = None
    for item in business["reviews"]:
        if item["_id"] == review_id:
            review = item
            break
    if review is None:
        return make_response(jsonify({"error": "Invalid review ID"}), 404)
    review["_id"] = str(review["_id"])
    return make_response(jsonify(review), 200)

@reviews_bp.route("/api/v1.0/businesses/<bid>/reviews/<rid>", methods=["PUT"])
@jwt_required
def edit_review(bid,rid):
    business_id = ObjectId(bid)
    business = businesses.find_one({"_id" : business_id})
    if business is None:
        return make_response(jsonify({"error" : "Invalid business ID"}), 404)

    review_id = ObjectId(rid)
    if not any(review["_id"] == review_id for review in business["reviews"]):
        return make_response(jsonify({"error" : "Invalid review ID"}), 404)

    if "username" not in request.form or \
       "comment" not in request.form or \
       "stars" not in request.form:
        return make_response(jsonify({"error" : "Missing form data"}), 404)

    edit_review = {
        "reviews.$.username" : request.form["username"],
        "reviews.$.comment" : request.form["comment"],
        "reviews.$.stars" : request.form["stars"]
    }
    result = businesses.update_one( \
        {"_id" : business_id, "reviews._id" : review_id}, \
        {"$set" : edit_review}
        )

    edited_review_url = \
    "http://localhost:5000/api/v1.0/businesses/" + \
    bid + "/reviews/" + rid
    return make_response(jsonify({"url" : edited_review_url}), 200)

@reviews_bp.route("/api/v1.0/businesses/<bid>/reviews/<rid>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_review(bid, rid):
    business_id = ObjectId(bid)
    business = businesses.find_one({"_id" : business_id})
    if business is None:
        return make_response(jsonify({"error" : "Invalid business ID"}), 404)

    review_id = ObjectId(rid)
    if not any(review["_id"] == review_id for review in business["reviews"]):
        return make_response(jsonify({"error" : "Invalid review ID"}), 404)

    businesses.update_one( 
        {"_id" : business_id, "reviews._id" : review_id},
        {"$pull" : {"reviews" : \
                    {"_id" : review_id}}})
    return make_response(jsonify({}), 204)