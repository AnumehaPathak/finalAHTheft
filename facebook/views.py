# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import re
import random
import requests
import pprint
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import *
from django.http import JsonResponse
# Create your views here.

VERIFY_TOKEN='AntiHomeTheft'

PAGE_ACCESS_TOKEN='EAAKa0eCWBu4BAJjbRJv4TN3GeAd0KNKRTNHFcmJW6HZCuwDsSyatiDZBVVp8Wyz6n5ZAhEvZCohgFy4qMVUrzwxV8ZArn9v824r3uWLdwoJw112XbMhHBHfA0TvkVZBeXfgwu0ZAh2rrmkAUYgS9DK43ZBbnwKz4KhwdXJOURh93xAZDZD'

live_global = False

@method_decorator(csrf_exempt)
def getResponse(request):

    print request.POST
    print request.POST.__dict__
    # print request.FILES
    if request.method == "POST":
        image = request.FILES.get('media')
        if image is not None:
            id_user=request.POST.get("id")
            #1490578364307193
            # import pdb; pdb.set_trace()
            fb_id = FacebookID.objects.get(pi_id=id_user).fb_id
            # fb_id = FacebookID(pi_id=id_user).fb_id
            post_facebook_message(fb_id,image,"hello")
        return HttpResponse("data received")
    else:
        return HttpResponse("request is not post")


def index(request):
    post_facebook_message("1531", "Hello")
    return HttpResponse('ok')

@method_decorator(csrf_exempt)
def kill(request):
    if request.method=="GET":
        # import pdb; pdb.set_trace()
        pi_id = request.GET.get('id')
        sender_id = FacebookID.objects.get(pi_id=pi_id).fb_id
        if Pi.objects.filter(fb_id=sender_id).exists():
            pi = Pi.objects.get(fb_id=sender_id)
            post_facebook_message_text(sender_id,"Shutting down pi.")
            return JsonResponse({'kill':pi.kill})
        else:
            return JsonResponse({'kill':False})
    return JsonResponse({'kill':False})


@method_decorator(csrf_exempt)
def live(request):
    if request.method=="GET":
        # import pdb; pdb.set_trace()
        pi_id = request.GET.get('id')
        sender_id = FacebookID.objects.get(pi_id=pi_id).fb_id
        if Live.objects.filter(fb_id=sender_id).exists():
            live = Live.objects.get(fb_id=sender_id)
            if live.live:
                send_fb_message("Pi is up and running")
                live_global = True
            return JsonResponse({'live':live.live})
        else:
            return JsonResponse({'live':False})
    return JsonResponse({'live':False})

def post_facebook_message(fbid,image,text):
    # image = default_storage.save('image.jpg', ContentFile(image.read()))
    image = ImageModel(image=image)
    image.save()
    image=image.image.url
    image="https://antihta.herokuapp.com"+image
    print image
    # import pdb;pdb.set_trace()
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg={
    "recipient":{
        "id":fbid
      },
      "message":{
        "attachment":{
          "type":"image",
          "payload":{
            "url":image
          }
        }
      }
    }       
    response_msg = json.dumps(response_msg)
    # import pdb;pdb.set_trace()
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

def post_facebook_message_text(fbid,text):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":text}})   
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

def find(title="girls"):
    url="http://api.tvmaze.com/singlesearch/shows?q=%s"%(title)
    resp = requests.get(url=url).text
    data = json.loads(resp)
    scoped_data=data["summary"]
    image_url=data["image"]["medium"]
    url_info=data['url']
    
    return scoped_data,image_url,url_info

class MyChatBotView(generic.View):
    def get(self,request,*args,**kwargs):
        if self.request.GET['hub.verify_token']==VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('oops invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self,request,*args,**kwargs):
        return generic.View.dispatch(self,request,*args,**kwargs)

    def post(self,request,*args,**kwargs):
        incoming_message=json.loads(self.request.body.decode('utf-8'))
        print incoming_message

        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    list_of_pi_kill_words = ["kill","shutdown","bye","goodbye"]
                    if message_text.isdigit():
                        if FacebookID.objects.filter(pi_id=message_text).exists():
                            fb_obj = FacebookID.objects.get(pi_id=message_text)
                            fb_obj.fb_id=sender_id
                            fb_obj.save()
                        else:
                            FacebookID.objects.create(pi_id=message_text,fb_id=sender_id).save()
                        # post_facebook_message(sender_id,message_text) 
                    elif message_text.lower() in list_of_pi_kill_words:
                        #shutdown pi
                        pi=None
                        if Pi.objects.filter(fb_id=sender_id).exists():
                            pi = Pi.objects.get(fb_id=sender_id)
                            pi.kill=True
                            pi.save()
                        else:
                            pi = Pi.objects.create(fb_id=sender_id,kill=True)
                            pi.save()
                        import time
                        time.sleep(7)
                        pi.kill=False;
                        pi.save()
                    else:
                        #internet response for pi
                        live=None
                        if Live.objects.filter(fb_id=sender_id).exists():
                            live = Live.objects.get(fb_id=sender_id)
                            live.live=True
                            live.save()
                        else:
                            live = Live.objects.create(fb_id=sender_id,live=True)
                            live.save()
                        import time
                        time.sleep(7)
                        live.live=False;
                        live.save()
                        if not live_global:
                            post_facebook_message_text(sender_id,"Pi not connected. Try restarting it.")
                        else:
                            live_global=False                    
                except Exception as e:
                    print e
                    pass

        return HttpResponse() 
