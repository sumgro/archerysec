#                   _
#    /\            | |
#   /  \   _ __ ___| |__   ___ _ __ _   _
#  / /\ \ | '__/ __| '_ \ / _ \ '__| | | |
# / ____ \| | | (__| | | |  __/ |  | |_| |
# /_/    \_\_|  \___|_| |_|\___|_|   \__, |
#                                    __/ |
#                                   |___/
# Copyright (C) 2017-2018 ArcherySec
# This file is part of ArcherySec Project.

from __future__ import unicode_literals
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from webscanners.models import burp_scan_result_db
from jiraticketing.models import jirasetting
from webscanners.models import webinspect_scan_db, \
    webinspect_scan_result_db
import hashlib


def webinspect_list_vuln(request):
    """
    webinspect Vulnerability List
    :param request:
    :return:
    """
    if request.method == 'GET':
        scan_id = request.GET['scan_id']
    else:
        scan_id = None

    webinspect_all_vul = webinspect_scan_result_db.objects.filter(
        scan_id=scan_id, vuln_status='Open')

    webinspect_all_vul_close = webinspect_scan_result_db.objects.filter(
        scan_id=scan_id, vuln_status='Close')

    return render(request,
                  'webinspectscanner/webinspect_list_vuln.html',
                  {'webinspect_all_vul': webinspect_all_vul,
                   'scan_id': scan_id,
                   'webinspect_all_vul_close': webinspect_all_vul_close
                   })


def webinspect_scan_list(request):
    """
    webinspect Scan List.
    :param request:
    :return:
    """
    all_webinspect_scan = webinspect_scan_db.objects.all()

    return render(request,
                  'webinspectscanner/webinspect_scan_lis.html',
                  {'all_webinspect_scan': all_webinspect_scan})


def webinspect_vuln_data(request):
    """
    webinspect Vulnerability Data.
    :param request:
    :return:
    """
    if request.method == 'GET':
        vuln_id = request.GET['vuln_id']
    else:
        vuln_id = None
    vuln_data = webinspect_scan_result_db.objects.filter(vuln_id=vuln_id)

    return render(request,
                  'webinspectscanner/webinspect_vuln_data.html',
                  {'vuln_data': vuln_data, })


def webinspect_vuln_out(request):
    """
    webinspect Vulnerability details.
    :param request:
    :return:
    """
    jira_url = None

    jira = jirasetting.objects.all()
    for d in jira:
        jira_url = d.jira_server

    if request.method == 'GET':
        scan_id = request.GET['scan_id']
        name = request.GET['scan_name']
    if request.method == "POST":
        false_positive = request.POST.get('false')
        status = request.POST.get('status')
        vuln_id = request.POST.get('vuln_id')
        scan_id = request.POST.get('scan_id')
        vuln_name = request.POST.get('vuln_name')
        webinspect_scan_result_db.objects.filter(vuln_id=vuln_id,
                                                 scan_id=scan_id).update(false_positive=false_positive,
                                                                         vuln_status=status)

        if false_positive == 'Yes':
            vuln_info = webinspect_scan_result_db.objects.filter(scan_id=scan_id, vuln_id=vuln_id)
            for vi in vuln_info:
                name = vi.name
                url = vi.vuln_url
                Severity = vi.severity_name
                dup_data = name + url + Severity
                false_positive_hash = hashlib.sha256(dup_data).hexdigest()
                webinspect_scan_result_db.objects.filter(vuln_id=vuln_id,
                                                         scan_id=scan_id).update(false_positive=false_positive,
                                                                                 vuln_status=status,
                                                                                 false_positive_hash=false_positive_hash
                                                                                 )

        return HttpResponseRedirect(
            '/webinspectscanner/webinspect_vuln_out/?scan_id=%s&scan_name=%s' % (scan_id, vuln_name))

    vuln_data = webinspect_scan_result_db.objects.filter(scan_id=scan_id,
                                                         name=name,
                                                         vuln_status='Open',
                                                         false_positive='No')
    vuln_data_closed = webinspect_scan_result_db.objects.filter(scan_id=scan_id,
                                                                name=name,
                                                                vuln_status='Closed',
                                                                false_positive='No')
    false_data = webinspect_scan_result_db.objects.filter(scan_id=scan_id,
                                                          name=name,
                                                          false_positive='Yes')

    return render(request,
                  'webinspectscanner/webinspect_vuln_out.html',
                  {'vuln_data': vuln_data,
                   'false_data': false_data,
                   'jira_url': jira_url,
                   'vuln_data_closed': vuln_data_closed
                   })


def del_webinspect_scan(request):
    """
    Delete webinspect Scans.
    :param request:
    :return:
    """
    if request.method == 'POST':
        scan_id = request.POST.get("scan_id")
        scan_url = request.POST.get("scan_url")

        scan_item = str(scan_id)
        value = scan_item.replace(" ", "")
        value_split = value.split(',')
        split_length = value_split.__len__()
        # print "split_length", split_length
        for i in range(0, split_length):
            scan_id = value_split.__getitem__(i)

            item = webinspect_scan_db.objects.filter(scan_id=scan_id
                                                     )
            item.delete()
            item_results = webinspect_scan_result_db.objects.filter(scan_id=scan_id)
            item_results.delete()
        messages.add_message(request, messages.SUCCESS, 'Deleted Scan')
        return HttpResponseRedirect('/webinspectscanner/webinspect_scan_list/')


def edit_webinspect_vuln(request):
    """
    The funtion Editing webinspect Vulnerability.
    :param request:
    :return:
    """
    if request.method == 'GET':
        id_vul = request.GET['vuln_id']
    else:
        id_vul = ''
    edit_vul_dat = burp_scan_result_db.objects.filter(vuln_id=id_vul).order_by('vuln_id')
    if request.method == 'POST':
        vuln_id = request.POST.get("vuln_id", )
        scan_id = request.POST.get("scan_id", )
        name = request.POST.get("name", )
        severity = request.POST.get("severity", )
        host = request.POST.get("host", )
        path = request.POST.get("path", )
        issuedetail = request.POST.get("issuedetail")
        description = request.POST.get("description", )
        solution = request.POST.get("solution", )
        location = request.POST.get("location", )
        vulnerabilityClassifications = request.POST.get("reference", )
        global vul_col
        if severity == 'High':
            vul_col = "important"
        elif severity == 'Medium':
            vul_col = "warning"
        elif severity == 'Low':
            vul_col = "info"
        else:
            vul_col = "info"
        print "edit_vul :", name

        webinspect_scan_result_db.objects.filter(vuln_id=vuln_id).update(
            name=name,
            severity_color=vul_col,
            severity=severity,
            host=host,
            path=path,
            location=location,
            issueDetail=issuedetail,
            issueBackground=description,
            remediationBackground=solution,
            vulnerabilityClassifications=vulnerabilityClassifications,
        )

        messages.add_message(request, messages.SUCCESS, 'Vulnerability Edited...')

        return HttpResponseRedirect("/webinspectscanner/webinspect_vuln_data/?vuln_id=%s" % vuln_id)

    return render(request, 'webinspectscanner/edit_webinspect_vuln.html', {'edit_vul_dat': edit_vul_dat})


def webinspect_del_vuln(request):
    """
    The function Delete the webinspect Vulnerability.
    :param request:
    :return:
    """
    if request.method == 'POST':
        vuln_id = request.POST.get("del_vuln", )
        un_scanid = request.POST.get("scan_id", )

        scan_item = str(vuln_id)
        value = scan_item.replace(" ", "")
        value_split = value.split(',')
        split_length = value_split.__len__()
        print "split_length", split_length
        for i in range(0, split_length):
            vuln_id = value_split.__getitem__(i)
            delete_vuln = webinspect_scan_result_db.objects.filter(vuln_id=vuln_id)
            delete_vuln.delete()
        webinspect_all_vul = webinspect_scan_result_db.objects.filter(scan_id=un_scanid)

        total_vul = len(webinspect_all_vul)
        total_critical = len(webinspect_all_vul.filter(severity_name='Critical'))
        total_high = len(webinspect_all_vul.filter(severity_name="High"))
        total_medium = len(webinspect_all_vul.filter(severity_name="Medium"))
        total_low = len(webinspect_all_vul.filter(severity_name="Low"))
        total_info = len(webinspect_all_vul.filter(severity_name="Information"))

        webinspect_scan_db.objects.filter(scan_id=un_scanid).update(
            total_vul=total_vul,
            critical_vul=total_critical,
            high_vul=total_high,
            medium_vul=total_medium,
            low_vul=total_low,
            info_vul=total_info
        )
        messages.success(request, "Deleted vulnerability")

        return HttpResponseRedirect("/webinspectscanner/webinspect_list_vuln?scan_id=%s" % un_scanid)
