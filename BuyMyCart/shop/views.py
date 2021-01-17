from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
# Create your views here.
MERCHANT_KEY = '############'
def index(request):
  #  products = Product.objects.all()
   ## print(products)
   # n = len(products)      # product length 
   # nSlides = n//4 + ceil((n/4)-(n//4))  # number of slides formula  



    #params = {'no_of_slides':nSlides,'range':range(1,nSlides),'product': products}
    #demo allproducts   allProds = [[products,range(1,nSlides), nSlides],[products,range(1,nSlides), nSlides]]
    allProds = []
    catprods = Product.objects.values('category', 'id')
    #print(catprods)
    cats = {item['category'] for item in catprods}
    #print(cats)
  #  price = Product.objects.values('price','product_name')
    #print(f"{price[4]['product_name']} = Rs. {price[4]['price']}")
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)      # product length 
        nSlides = n//4 + ceil((n/4)-(n//4))  
        allProds.append([prod, range(1,nSlides), nSlides])
        #print(allProds)
    #print(allProds)
    print(prod)
    params = {'allProds':allProds}
    #print(params)
    
    return render(request,'shop/index_s.html',params)
def searchMatch(query,item):
    '''return true if only query match the item'''
    query=query.lower()
    if query in (item.desc).lower() or query in (item.product_name).lower() or query in (item.category).lower():
        return True
    else:
        return False
def search(request):
    query = request.GET.get('search',)
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)] # search function return boolean if match the item then return true or false
        
        n = len(prod)      # product length 
        nSlides = n//4 + ceil((n/4)-(n//4))  
        if len(prod)!=0:
            allProds.append([prod, range(1,nSlides), nSlides])
        #print(allProds)
   
    params = {'allProds':allProds,"msg":""}
    if len(allProds)==0 or len(query)<3:
        params = {'msg':"item not found related to your search"}
    return render(request,'shop/search.html',params)


def about(request):
    return render(request,'shop/about.html')

def contact(request):
    thank=False
    
    if request.method == "POST":
      #  print(request) # response printed here
        name= request.POST.get('name', '')
        email= request.POST.get('email', '')
        phone= request.POST.get('phone', '')
        desc= request.POST.get('desc', '')
        print(name, email, phone, desc)
        contac = Contact(name=name, email=email, phone=phone, desc=desc)  # name=  ---> database ka hai and = name ye wala variable wala hai  
        contac.save()
        thank = True
        return render(request,'shop/contact.html', {'thank':thank})
    return render(request, 'shop/contact.html')


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates":updates, "itemsJson":order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')

        except Exception as e:
            print(e)
            return HttpResponse('{"status":"error"}')
                
                

    return render(request,'shop/tracker.html')


def productView(request,myid):
    # fetch the product using this id
    product = Product.objects.filter(id=myid)
    print(product)
    return render(request,'shop/prodView.html',{'product': product[0]})  #[0] kyoki list hai is [0] ek item jaaye  'product'--- is naam se acces karneg : product ye variable wala product hai

def checkout(request):
    if request.method == "POST":
        #print(request) # response printed here
        items_json = request.POST.get('itemsJson', '')
        name= request.POST.get('name', '')
        amount= request.POST.get('amount', '')
        print(amount)
        email= request.POST.get('email', '')
        address= request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city= request.POST.get('city', '')
        state= request.POST.get('state', '')
        zip_code= request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        print(name,email,phone)
        order = Orders(items_json=items_json,name=name, email=email, address=address,city=city,state=state,zip_code=zip_code,phone=phone,amount=amount )  # name=  ---> database ka hai and = name ye wala variable wala hai  
        order.save()
        update = OrderUpdate(order_id=order.order_id,update_desc="The order has been placed ")
        update.save()
        thank = True
        id = order.order_id
        #return render(request,'shop/checkout.html',{'thank':thank,'id':id})
        #request paytm to transfer the amount to your acoount after payment by user
        param_dict = {
            'MID':'mMpjcS15874147240938',
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':'email',
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/Shop/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict,MERCHANT_KEY)
        print(param_dict['MID'])
        print(param_dict['ORDER_ID'])
        print(param_dict['CALLBACK_URL'])
        return render(request,'shop/paytm.html',{'param_dict':param_dict})
         
    return render(request,'shop/checkout.html/') 

@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum) # ye btayga ki respose hai ki nahi paytm ne diya hua hai verify_checksum function
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order is not successful'+ response_dict['RESPMSG'])            

    return render(request,'shop/paymentstatus.html',{'response':response_dict})
    # paytm will send you post request ..... (csrf xmnt karna hai) #import decorators csrf 
    

