from django.shortcuts import render
from ddm.models import DataSource
from django.db.models import Count,Sum,Func,FloatField,Avg
from colorhash import ColorHash
from ddm.utils import DDModel

class Round(Func):
  function = 'ROUND'
  arity = 2


def ddm_chart_view(request):
    dataset = request.GET.get('dataset',None)
    value = request.GET.get('value',None)
    axis_a = request.GET.get('axis_a',None)
    axis_b = request.GET.get('axis_b',None)
    ctype= request.GET.get('ctype',None)
    operation= request.GET.get('operation','count')
    MODEL = DDModel(dataset)
    datasource = DataSource.objects.filter(model=dataset).first()
    field_map = datasource.field_map
    
    for field,fdata in field_map.items():
        if fdata[0] == value:
            value = field
            break
    
    for field,fdata in field_map.items():
        if fdata[0] == axis_a:
            axis_a = field
            break
    
    for field,fdata in field_map.items():
        if fdata[0] == axis_b:
            axis_b = field
    if axis_a:
        if operation == 'sum':
            queryset = MODEL.objects.all().values(axis_a).annotate(count=Round(Sum(value),2,output_field=FloatField()))
        elif operation == 'avg':
            queryset = MODEL.objects.all().values(axis_a).annotate(count=Round(Avg(value),2,output_field=FloatField()))
        else:
            queryset = MODEL.objects.all().values(axis_a).annotate(count=Count(value))
        response = {'labels':[],'data':[],'colors':[]}
        for data in queryset:
            response['labels'].append(data[axis_a])
            response['data'].append(data['count'])
            response['colors'].append(ColorHash(data[axis_a]).hex)
        if axis_b and ctype=='bar':
            if operation == 'sum':
                queryset = MODEL.objects.all().values(axis_a,axis_b).annotate(count=Round(Sum(value),2,output_field=FloatField())).order_by(axis_b)
            elif operation == 'avg':
                queryset = MODEL.objects.all().values(axis_a,axis_b).annotate(count=Round(Avg(value),2,output_field=FloatField())).order_by(axis_b)
            else:
                queryset = MODEL.objects.all().values(axis_a,axis_b).annotate(count=Count(value)).order_by(axis_b)
            result = {}
            labels = set()
            for data in queryset:
                if data[axis_b] not in result.keys():
                    result[data[axis_b]]={}
                if data[axis_a] not in result[data[axis_b]].keys():
                    result[data[axis_b]][data[axis_a]]=data['count']
                    labels.add(data[axis_a])
            cresponse = {}
            for key,data in result.items():
                cresponse[key] = []
                for label in labels:
                    if label in data.keys():
                        cresponse[key].append(data[label])
                    else:
                        cresponse[key].append(0)
                    
            response = {'data':[],'label':list(labels)}
            for key,cdata in cresponse.items():
                response['data'].append({'name':key,'data':cdata})

    else:
        if operation == 'sum':
            queryset = MODEL.objects.all().aggregate(count=Round(Sum(value),2,output_field=FloatField()))
        else:
            queryset = MODEL.objects.all().aggregate(count=Count(value))
        
        response = {'data':[queryset['count']],'labels':[value]}
    print(queryset)
    context={"cdata":response,"ctype":ctype,'axis_a':axis_a,'axis_b':axis_b}

    return render(request, "chart.html", context)

