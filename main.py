#Import the FastAPI framework
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field

# Create an instance of the FastAPI class
app = FastAPI()

#----------QUESTION 6----------#
#----------PYDANTIC MODEL----------#
class EnrollRequest(BaseModel):
    member_name:str=Field(...,min_length=2)
    plan_id:int=Field(...,gt=0)
    phone : str = Field(...,min_length=10)
    start_month : str = Field(...,min_length=3)
    payment_mode : str = Field(default="cash")
    referral_code : str = Field(default="") # Added from Question 9


#----------QUESTION 11----------#
#----------PYDANTIC MODEL -2 ----------#
class NewPlan(BaseModel): # Model for creating a new gym membership plan
    name:str=Field(...,min_length=3)
    duration_months:int=Field(...,gt=0)
    price:int=Field(...,gt=0)
    includes_classes:bool=Field(default=False)
    includes_trainer:bool=Field(default=False)

#----------QUESTION 7----------#
# Helper function to find a plan by its ID
def find_plan(plan_id:int):
    for plan in plans:
        if plan["id"]==plan_id:
            return plan
    return None

# Helper function to calculate the fees based on the plan and payment method
def calculate_membership_fee(base_price:int,duration_months:int,payment_mode:str,referral_code:str=""):
    discount = 0
    if duration_months >= 12:
        discount = 0.20
    elif duration_months>=6:
        discount = 0.10
    
    discounted_price = base_price*(1-discount)

    referral_discount_amount=0

    if referral_code:
        referral_discount_amount = discounted_price * 0.05 # Calculate the referral discount amount
        discounted_price -= referral_discount_amount # Apply the referral discount

    processing_fee=200 if payment_mode.lower()=="emi" else 0
    total_fee = discounted_price+processing_fee

    return{
        "base_price":base_price,
        "discount_applied":discount*100,
        "referral_discount":5 if referral_code else 0,
        "referral_discount_amount":referral_discount_amount,
        "discounted_price":discounted_price,
        "processing_fee":processing_fee,
        "total_fee":total_fee
    }

#----------QUESTION 10----------#
# Helper function to filter plans based on query parameters
def filter_plans_logic(max_price=None,max_duration=None,includes_classes=None,includes_trainer=None):

    filtered_plans = plans

    if max_price is not None:
        filtered_plans = [plan for plan in filtered_plans if plan["price"] <= max_price]

    if max_duration is not None:
        filtered_plans = [plan for plan in filtered_plans if plan["duration_months"] <= max_duration]

    if includes_classes is not None:
        filtered_plans = [plan for plan in filtered_plans if plan["includes_classes"] == includes_classes]

    if includes_trainer is not None:
        filtered_plans = [plan for plan in filtered_plans if plan["includes_trainer"] == includes_trainer]

    return filtered_plans

#----------Question 1----------#
# Root endpoint that returns a welcome message
@app.get("/")
def home():
    return {"message": "Welcome to IronFit Gym!"}

# Gym Membership Plans Data
plans=[{"id":1,"name":"Basic","duration_months":1,"price":1000,"includes_classes":False,"includes_trainer":False},
       {"id":2,"name":"Standard","duration_months":3,"price":2500,"includes_classes":True,"includes_trainer":False},
       {"id":3,"name":"Premium","duration_months":6,"price":4500,"includes_classes":True,"includes_trainer":True},
       {"id":4,"name":"Elite","duration_months":12,"price":8000,"includes_classes":True,"includes_trainer":True},
       {"id":5,"name":"Ultimate","duration_months":14,"price":11000,"includes_classes":True,"includes_trainer":True},
]

#----------Question 2----------#
# Endpoint to get all gym membership plans and the minimum price and the maximum price among the plans
@app.get("/plans")
def get_plans():
    prices = [plan["price"] for plan in plans] # Extract the prices from the plans
    min_price = min(prices)                    # Find the minimum price
    max_price = max(prices)                    # Find the maximum price
    total_plans=len(plans)                     # Get the total number of plans

    return{
        "plans":plans,
        "total":total_plans,
        "price_ranges":{
            "min_price":min_price,
            "max_price":max_price
        }
    }

#----------Question 5----------#
# Endpoint to get summary of all gym membership plans.
@app.get("/plans/summary")
def get_plans_summary():
    total_plans=len(plans)
    class_included_plans = [plan for plan in plans if plan["includes_classes"]]
    trainer_included_plans = [plan for plan in plans if plan["includes_trainer"]]
    cheapest_plan = min(plans, key=lambda x: x["price"])
    expensive_plan = max(plans, key=lambda x: x["price"])
    return{
        "total_plans": total_plans,
        "plans_including_classes": len(class_included_plans),
        "plans_including_trainer": len(trainer_included_plans),
        "cheapest_plan":{
            "name":cheapest_plan["name"],
            "price":cheapest_plan["price"]
        },
        "most_expensive_plan": {
            "name": expensive_plan["name"],
            "price": expensive_plan["price"]
        }
    }
#----------Question 10----------#
# Endpoint to filter gym membership plans based on query parameters
@app.get("/plans/filter")
def filter_plans(max_price: int = None, 
                 max_duration: int = None, 
                 includes_classes: bool = None, 
                 includes_trainer: bool = None
                 ):

    result=filter_plans_logic(max_price, max_duration, includes_classes, includes_trainer)

    return {
        "filtered_plans": result,
        "total": len(result)
    }
#-------Question 16----------#
# Endpoint to search for a plan by keyword
@app.get("/plans/search")
def search_plans(keyword:str):
    keyword=keyword.lower()
    results=[]

    if keyword=="classes":
        results=[plan for plan in plans if plan["includes_classes"]]

    elif keyword=="trainer":
        results=[plan for plan in plans if plan["includes_trainer"]]

    else:
        results=[plan for plan in plans if keyword in plan["name"].lower()]

    return {
        "results":results,
        "total":len(results)
    }

#----------Question 17----------#
# Endpoint to sort
@app.get("/plans/sort")
def sort_plans(sort_by:str="price"):

    valid_fields=["price","name","duration_months"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f"Error : Invalid sort field. Valid options are {valid_fields}")
    sorted_plans=sorted(plans, key=lambda x: x[sort_by])
    return {
        "sorted_by":sort_by,
        "plans":sorted_plans
    }

#----------Question 18----------#
# Endpoint for pagination of plans
@app.get("/plans/page")
def paginate_plans(page:int=1, limit:int=2):
    total_plans=len(plans)
    total_pages=(total_plans+limit-1)//limit
    if page<1 or page>total_pages:
        raise HTTPException(status_code=400,detail=f"Error : Invalid page number. Valid page numbers are between 1 and {total_pages}")

    start=(page-1)*limit
    end=start+limit
    paginated_data=plans[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_plans": total_plans,
        "total_pages": total_pages,
        "plans": paginated_data
    }

#----------Question 20----------#
@app.get("/plans/browse")
def browse_plans(
    keyword: str = None,
    includes_classes: bool = None,
    includes_trainer: bool = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 2):

    data=plans
    if keyword:
        keyword=keyword.lower()

        if keyword=="classes":
            data=[plan for plan in data if plan["includes_classes"]]
        elif keyword=="trainer":
            data=[plan for plan in data if plan["includes_trainer"]]
        else:
            data=[plan for plan in data if keyword in plan["name"].lower()]
            
    if includes_classes is not None:
        data=[plan for plan in data if plan["includes_classes"]==includes_classes]

    if includes_trainer is not None:
        data=[plan for plan in data if plan["includes_trainer"]==includes_trainer]
    
    valid_sort_fields=["price","name","duration_months"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400,detail=f"Error : Invalid sort field. Valid options are {valid_sort_fields}")
    reverse_order=True if order=="desc" else False
    data=sorted(data, key=lambda x: x[sort_by], reverse=reverse_order)
    total=len(data)
    total_pages=(total+limit-1)//limit
    if page<1 or page>total_pages:
        raise HTTPException(status_code=400,detail=f"Error : Invalid page number. Valid page numbers are between 1 and {total_pages}")
    start=(page-1)*limit
    end=start+limit
    paginated_data=data[start:end]
    return {
        "filters":{
            "keyword": keyword,
            "includes_classes": includes_classes,
            "includes_trainer": includes_trainer,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit
        },
        "total_results": total,
        "total_pages": total_pages, 
        "plans": paginated_data
    }

#----------Question 3----------#
# Endpoint to get a specific gym membership plan by its ID
@app.get("/plans/{plan_id}")
def get_plan(plan_id: int): # Function to fetch a specific plan by its ID
    for plan in plans:
        if plan["id"]==plan_id:
            return plan
        
    raise HTTPException(status_code=404,detail="Error : Plan not found") #If the plan does not exist we return an error message with a 404 status code

#----------Question 19----------#
# Endpoint to search for memberships
@app.get("/memberships/search")
def search_memberships(member_name: str):
    results = [membership for membership in memberships if member_name.lower() in membership["member_name"].lower()]

    return {
        "results": results,
        "total": len(results)
    }

# Endpoint to sort memberships
@app.get("/memberships/sort")
def sort_memberships(sort_by: str = "total_fee"):
    valid_fields = ["total_fee", "duration_months"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Error: Invalid sort field. Valid options are {valid_fields}")
    
    sorted_data = sorted(memberships, key=lambda x: x[sort_by])
    return {
        "sorted_by": sort_by,
        "memberships": sorted_data
    }

# Endpoint for pagination of memberships
@app.get("/memberships/page")
def paginate_memberships(page: int = 1, limit: int = 2):
    total_memberships = len(memberships)
    total_pages = (total_memberships + limit - 1) // limit
    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail=f"Error: Invalid page number. Valid page numbers are between 1 and {total_pages}")

    start = (page - 1) * limit
    end = start + limit
    paginated_data = memberships[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_memberships": total_memberships,
        "total_pages": total_pages,
        "memberships": paginated_data
    }

#----------Question 4----------#
memberships=[] # This will be used to store all user memberships
membership_counter=1 # This will be used to assign a unique ID to each membership

class_bookings=[] # Added for Question 14 to store class bookings
class_counter=1
# Endpoint to return all user memberships and total count.
@app.get("/memberships")
def get_memberships():
    return {
        "memberships":memberships,
        "total":len(memberships)
    }

#----------POST--------------#
#----------Question 8----------#
@app.post("/memberships")
def create_membership(request:EnrollRequest):
    global membership_counter
    # Check if the plan exists
    plan = find_plan(request.plan_id)
    if not plan:
        raise HTTPException(status_code=404,detail="Error : Plan not found")
    
    # We calculate fees
    fee_details = calculate_membership_fee(
        base_price=plan["price"],
        duration_months=plan["duration_months"],
        payment_mode=request.payment_mode,
        referral_code=request.referral_code
    )

    # Calculate monthly fee
    monthly_cost = fee_details["total_fee"]/plan["duration_months"]

    # Create membership object
    new_membership={
        "membership_id":membership_counter,
        "member_name":request.member_name,
        "plan_name":plan["name"],
        "duration_months":plan["duration_months"],
        "monthly_cost":round(monthly_cost, 2),
        "total_fee":fee_details["total_fee"],
        "status":"active",
        "fee_breakdown":fee_details # Added from Question 9 
    }

    # Store membership
    memberships.append(new_membership)

    #Increment Counter
    membership_counter+=1

    return new_membership

#----------Question 11----------#
# Endpoint to create a new gym membership plan
@app.post("/plans",status_code=201)
def create_plan(plan:NewPlan):
    for existing in plans:
        if existing["name"].lower()==plan.name.lower():
            raise HTTPException(status_code=400,detail="Error : Plan with this name already exists")

    # Generate new ID
    new_id=max(plan["id"] for plan in plans)+1

    # Create plan object
    new_plan={
        "id":new_id,
        "name":plan.name,
        "duration_months":plan.duration_months,
        "price":plan.price,
        "includes_classes":plan.includes_classes,
        "includes_trainer":plan.includes_trainer
    }

    # Add to list
    plans.append(new_plan)
    return new_plan

#----------PUT----------#
#----------Question 12----------#
@app.put("/plans/{plan_id}")
def update_plan(plan_id:int,
                price:int=None,
                includes_classes:bool=None,
                includes_trainer:bool=None
                ):
            
        # Find the plan
        for plan in plans:
            if plan["id"]==plan_id:
                if price is not None:
                    plan["price"]=price
                if includes_classes is not None:
                    plan["includes_classes"]=includes_classes
                if includes_trainer is not None:
                    plan["includes_trainer"]=includes_trainer
                return {
                    "message":"Plan updated successfully",
                    "updated_plan":plan
                }
        # If plan not found
        raise HTTPException(status_code=404,detail="Error : Plan not found")

#----------DELETE----------#
#----------Question 13----------#
@app.delete("/plans/{plan_id}")
def delete_plan(plan_id:int):

    # Find the plan
    for plan in plans:
        if plan["id"]==plan_id:

            # Check if any active membership uses this plan
            for m in memberships:
                if m["plan_name"].lower()==plan["name"].lower() and m["status"]=="active":
                    raise HTTPException(status_code=400,detail="Error : Cannot delete plan with active memberships")

            # Delete the plan
            plans.remove(plan)

            return {"message":"Plan deleted successfully"}

    # If plan not found
    raise HTTPException(status_code=404,detail="Error : Plan not found")

#----------Question 14----------#
@app.post("/classes/book")
def book_class(member_name:str, class_name:str,class_date:str):
    global class_counter

    # Check if member has an active membership
    member_membership = None
    for m in memberships:
        if m["member_name"].lower()==member_name.lower() and m["status"]=="active":
            member_membership=m
            break

    if not member_membership:
        raise HTTPException(status_code=400,detail="Error : No active membership found")

    # Check if plan includes classes
    for plan in plans:
        if plan["name"].lower()==member_membership["plan_name"].lower():
            if not plan["includes_classes"]:
                raise HTTPException(status_code=400,detail="Error : Your membership plan does not include classes")
    
    # Create booking
    booking={
        "booking_id":class_counter,
        "member_name":member_name,
        "class_name":class_name,
        "class_date":class_date
    }

    class_bookings.append(booking)
    class_counter+=1

    return {
        "message":"Class booked successfully",
        "booking_details":booking
    }

@app.get("/classes/bookings")
def get_class_bookings():
    return {
        "class_bookings":class_bookings,
        "total":len(class_bookings)
    }

#----------Question 15----------#
# Endpoint to cancel a class booking by its ID
@app.delete("/classes/bookings/{booking_id}")
def cancel_class_booking(booking_id:int):
    global class_counter

    # Find the booking
    for booking in class_bookings:
        if booking["booking_id"]==booking_id:
            class_bookings.remove(booking)
            class_counter-=1
            return {"message":"Class booking cancelled successfully"}

    # If booking not found
    raise HTTPException(status_code=404,detail="Error : Booking not found")

# Endpoint to freeze a membership
@app.put("/memberships/{membership_id}/freeze")
def freeze_membership(membership_id:int):
    for membership in memberships:
        if membership["membership_id"]==membership_id:
            membership["status"]="frozen"
            return {
                "message":"Membership frozen successfully"}

    raise HTTPException(status_code=404,detail="Error : Membership not found")

# Endpoint to reactivate a frozen membership
@app.put("/memberships/{membership_id}/reactivate")
def reactivate_membership(membership_id:int):
    for membership in memberships:
        if membership["membership_id"]==membership_id:
            membership["status"]="active"
            return {
                "message":"Membership reactivated successfully"}

    raise HTTPException(status_code=404,detail="Error : Membership not found")
