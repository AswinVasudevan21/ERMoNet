from flask import Flask, render_template, jsonify, request, send_file
from werkzeug.utils import redirect

from BotoFramework import BotoFramework
from JsonParser import JsonParser
from DatabaseHelper import DatabaseHelper
from JsonValidator import JsonValidator
from AutoRoutine import AutoRoutine
from CsvGenerator import CsvGenerator
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)


# Index

@app.route('/', methods=['GET', 'POST'])
def index():
    global url
    try:
        if request.method == 'POST':
            got_json = request.get_json()
            validate_task = JsonValidator(got_json)

            if validate_task.checkRequestValid():
                req_task = JsonParser(got_json)
                req_task.parseJson()
                create_database = DatabaseHelper()
                if (req_task.task_json == "binary") and (req_task.annotation_unit == "image"):
                    if req_task.iscategorical:
                        url = create_database.writeDatabaseCategorical(req_task)
                    else:
                        url = create_database.writeDatabase(req_task)
                else:
                    if (req_task.task_json == "binary") and (req_task.annotation_unit == "image_set"):
                        if req_task.iscategorical:
                            url = create_database.writeSetDatabaseCategorical(req_task)
                        else:
                            url = create_database.writeSetDatabase(req_task)

                if (req_task.task_json == "tertiary") and (req_task.annotation_unit == "image"):
                    if req_task.iscategorical:
                        url = create_database.writeTertiaryDatabaseCategorical(req_task)
                    else:
                        url = create_database.writeTertiaryDatabase(req_task)
                else:
                    if (req_task.task_json == "video"):
                            url = create_database.writeVideoDatabaseCategorical(req_task)


                return url
            else:
                return "error"

        else:
            return render_template('home.html')

    except:
        return render_template('error.html')

#Chunk

@app.route('/chunk/<string:task_id>', methods=['GET', 'POST'])
def indexchunk(task_id):
    try:
        if request.method == 'POST':
            got_json = request.get_json()
            validate_task = JsonValidator(got_json)

            if validate_task.checkRequestValid():
                req_task = JsonParser(got_json)
                req_task.parseJson()
                create_database = DatabaseHelper()
                if (req_task.task_json == "binary") and (req_task.annotation_unit == "image"):
                    if req_task.iscategorical:
                        url = create_database.writeDatabaseChunkCategorical(req_task, task_id)
                    else:
                        url = create_database.writeDatabaseChunk(req_task, task_id)
                    view_str = "https://annsen.herokuapp.com/view/" + url + "/" + "1"
                else:
                    if (req_task.task_json == "binary") and (req_task.annotation_unit == "image_set"):
                        if req_task.iscategorical:
                            url = create_database.writeSetDatabaseChunkCategorical(req_task, task_id)
                        else:
                            url = create_database.writeSetDatabaseChunk(req_task, task_id)
                        view_str = "https://annsen.herokuapp.com/binarysetview/" + url + "/" + "1"

                if (req_task.task_json == "tertiary") and (req_task.annotation_unit == "image"):
                    if req_task.iscategorical:
                        url = create_database.writeTertiaryDatabaseChunkCategorical(req_task, task_id)
                    else:
                        url = create_database.writeTertiaryDatabaseChunk(req_task, task_id)
                    view_str = "https://annsen.herokuapp.com/tertiaryview/" + url + "/" + "1"

                if (req_task.task_json == "video"):
                    url = create_database.writeVideoDatabaseChunkCategorical(req_task, task_id)
                    view_str = "https://annsen.herokuapp.com/videoview/" + url + "/" + "1"


                return jsonify({"share": "https://annsen.herokuapp.com/register/" + url, "view": view_str })
            else:
                return jsonify({"json": "error"})

        else:
            return render_template('home.html')

    except Exception as e:
        print(e)
        return render_template('error.html')


# Register

@app.route('/register/<string:task_id>', methods=['GET', 'POST'])
def do_register(task_id):
    try:
        if request.method == 'POST':
            try:
                username = request.form['email']
                get_database = DatabaseHelper()
                task_type = get_database.getTaskType(task_id)
                pages_per_annotator = get_database.getPagesPerAnnotator(task_id)
                start_page = get_database.getStartPageNumber(task_id)
                max_duration = get_database.getMaxDuration(task_id)
                start_time = datetime.utcnow()
                max_time = start_time + timedelta(seconds=int(max_duration))
                userid = get_database.updateRegisterDatabase(username, task_id, pages_per_annotator, start_page,
                                                             start_time,
                                                             max_time)
                min_page = str(get_database.getStartPageAnnotation(task_id, userid))
                req_type = "redirect"

                if task_type == "binary":
                    url = "https://annsen.herokuapp.com/single/" + task_id + "/" + userid + "/" + req_type + "/" + min_page
                else:
                    if task_type == "binaryset":
                        url = "https://annsen.herokuapp.com/binaryset/" + task_id + "/" + userid + "/" + req_type + "/" + min_page

                if task_type == "tertiary":
                    url = "https://annsen.herokuapp.com/tertiary/" + task_id + "/" + userid + "/" + req_type + "/" + min_page

                if task_type == "video":
                    url = "https://annsen.herokuapp.com/video/" + task_id + "/" + userid + "/" + req_type + "/" + min_page

                return redirect(url)
            except Exception as e:
                print(e)
                return render_template('completed.html')

        else:
            request_database = DatabaseHelper()
            task_type = request_database.getTitle(task_id)
            pages_per_annotator = request_database.getPagesPerAnnotator(task_id)
            max_duration = request_database.getMaxDuration(task_id)
            return render_template('registration.html', tasktype=task_type, count=pages_per_annotator,
                                   time=max_duration, url=task_id)

    except:
        return render_template('error.html')


# Single Image

@app.route('/single/<string:task_id>/<string:userid>/<string:req_type>/<string:min_page>', methods=['GET', 'POST'])
def do_single(task_id, userid, req_type, min_page):
    try:
        global marked, all_marked, email
        marked = []
        all_marked = []
        get_single_database = DatabaseHelper()
        if request.method == 'GET':
            if req_type == "redirect":
                pages_per_annotator = get_single_database.getPagesPerAnnotator(task_id)
                user_id = userid
                email = get_single_database.getEmail(user_id)
                categorical_task = get_single_database.getCategoryPosition(task_id)
                is_local = get_single_database.getLocal(task_id)
                try:
                    min_page_db = get_single_database.getFirstPage(task_id, email, user_id)
                    last_page_db = get_single_database.getLastPage(task_id)
                    max_duration = get_single_database.getMaxDuration(task_id)
                    max_page = int(min_page_db) + int(pages_per_annotator)
                    questions = get_single_database.getQuestions(task_id, email, min_page)
                    get_url_boto = BotoFramework()

                    if is_local == "true":
                        list_questions = []
                        for i in questions:
                            list_questions.append(i[0])
                        temp_url = list_questions
                    else:
                        temp_url = get_url_boto.getTempUrl(questions, max_duration)

                    title = get_single_database.getTitle(task_id)
                    instruction = get_single_database.getInstructions(task_id)
                    img_id = get_single_database.getImageid(task_id, email, min_page)
                    total_len = len(temp_url)

                    mark_id = get_single_database.getMarkedImageid(task_id, email, min_page)
                    mark_len = len(mark_id)

                except:
                    max_page = int(pages_per_annotator)
                    pass

                max_time = get_single_database.getMaxTime(task_id, user_id)
                current_time = datetime.now()

                dt = datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f")
                dt_round_microsec = round(dt.microsecond / 1000000)
                dt = dt.replace(microsecond=dt_round_microsec)
                maxtime_js = datetime.strftime(dt, "%b %d, %Y %H:%M:%S")


                if current_time < datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f"):
                    if int(min_page) > max_page:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                               taskid=task_id,
                                               raiser=raiser, userid=user_id)

                    if int(min_page) == last_page_db + 1:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator, taskid=task_id,
                                               raiser=raiser, userid=user_id)
                    if int(min_page) < max_page:
                        remaining = max_page - int(min_page)
                        if categorical_task > 0:
                            categories = get_single_database.getCategories(task_id)
                            categorytype = get_single_database.getAllCategoryTypes(task_id)

                            category_list = []
                            categorytype_list = []

                            for i in range(0, len(categories)):
                                category_list.append(categories[i][0].split())
                                categorytype_list.append(categorytype[i][0].split())

                            category_len = len(category_list)
                            categorysub_len = []
                            for j in range(0, category_len):
                                categorysub_len.append(len(category_list[j]))
                            try:
                                marked_category = get_single_database.getMarkedCategories(task_id, min_page)
                                marked_category_list = marked_category[0][0].split()
                                marked_category_len = len(marked_category_list)

                                marked_single_category = get_single_database.getMarkedSingleCategories(task_id,
                                                                                                       min_page)
                                marked_single_list = marked_single_category[0][0].split()
                                marked_single_len = len(marked_single_list)
                            except:
                                marked_category_list = []
                                marked_category_len = 0
                                marked_single_list = []
                                marked_single_len = 0
                                pass

                            return render_template('singlecategorical.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, category=category_list,
                                                   categorytype=categorytype_list,
                                                   categorylen=category_len, categorysublen=categorysub_len,
                                                   markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len,
                                                   maxduration=maxtime_js, remaining=remaining)
                        else:
                            return render_template('singletest.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                                   mark=mark_id, marklen=mark_len, remaining=remaining, maxduration=maxtime_js)
                    else:
                        if int(min_page) == max_page:
                            raiser = get_single_database.getRaiserName(task_id)
                            return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                                   taskid=task_id,
                                                   raiser=raiser, userid=user_id)

                        else:
                            return render_template('error.html')
                else:
                    get_single_database.setNoneRegister(task_id, user_id)
                    return render_template('expired.html')
            else:
                all_marked = request.get_json()
                return "ok"


        else:
            all_marked = request.get_json()
            img_id_mark = all_marked['marked']
            get_single_database.setSingleFalseAnnotationResult(email, task_id, min_page)
            get_single_database.updateAnnotationResult(email, task_id, img_id_mark)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_single_database.setCategoryResult(task_id, min_page, checkboxes)
                get_single_database.setNoneSingleResult(task_id, min_page, "Na")
                get_single_database.setSingleResult(task_id, min_page, radioboxes)
            except:
                pass

            return "okay"

    except Exception as e:
        print(e)
        return render_template('error.html')


# Binary Set Image

@app.route('/binaryset/<string:task_id>/<string:userid>/<string:req_type>/<string:min_page>', methods=['GET', 'POST'])
def do_set(task_id, userid, req_type, min_page):
    try:
        global marked, all_marked, email
        marked = []
        all_marked = []
        get_single_database = DatabaseHelper()
        if request.method == 'GET':
            if req_type == "redirect":

                pages_per_annotator = get_single_database.getPagesPerAnnotator(task_id)
                user_id = userid
                email = get_single_database.getEmail(user_id)
                categorical_task = get_single_database.getCategoryPosition(task_id)
                is_local = get_single_database.getLocal(task_id)

                try:
                    min_page_db = get_single_database.getFirstPage(task_id, email, user_id)
                    last_page_db = get_single_database.getLastPage(task_id)
                    max_duration = get_single_database.getMaxDuration(task_id)
                    max_page = int(min_page_db) + int(pages_per_annotator)
                    questions = get_single_database.getQuestions(task_id, email, min_page)
                    get_url_boto = BotoFramework()
                    if is_local == "true":
                        list_questions = []
                        for i in questions:
                            list_questions.append(i[0])
                        temp_url = list_questions
                    else:
                        temp_url = get_url_boto.getTempUrl(questions, max_duration)

                    total_len = len(temp_url)

                    max_set = get_single_database.getMaxSet(task_id, email, min_page)
                    min_set = get_single_database.getMinSet(task_id, email, min_page)
                except:
                    max_page = int(pages_per_annotator)
                    pass

                try:
                    set_len = get_single_database.getSetLength(task_id, email, max_set, min_set, min_page)
                    list_set_len = len(set_len)

                    imgid_set = get_single_database.getImgIdSet(task_id, email, min_page, max_set, min_set)
                    imgset_len = len(imgid_set)

                    list_imgid_set = [[] for _ in range(imgset_len)]
                    for i in range(0, imgset_len):
                        for j in range(0, len(imgid_set[i])):
                            list_imgid_set[i].append(imgid_set[i][j][0])
                    title = get_single_database.getTitle(task_id)
                    instruction = get_single_database.getInstructions(task_id)
                    img_id = get_single_database.getImageid(task_id, email, min_page)
                    mark_id = get_single_database.getMarkedImageid(task_id, email, min_page)
                    mark_len = len(mark_id)
                except:
                    list_set_len = 0
                    list_imgid_set = [[]]
                    imgset_len = []
                    pass

                max_time = get_single_database.getMaxTime(task_id, user_id)
                current_time = datetime.now()

                dt = datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f")
                dt_round_microsec = round(dt.microsecond / 1000000)
                dt = dt.replace(microsecond=dt_round_microsec)
                maxtime_js = datetime.strftime(dt, "%b %d, %Y %H:%M:%S")

                if current_time < datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f"):
                    if int(min_page) > max_page:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                               taskid=task_id,
                                               raiser=raiser, userid=user_id)
                    if int(min_page) == last_page_db + 1:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator, taskid=task_id,
                                               raiser=raiser, userid=user_id)
                    if int(min_page) < max_page:
                        remaining = max_page - int(min_page)
                        if categorical_task > 0:
                            categories = get_single_database.getCategories(task_id)
                            categorytype = get_single_database.getAllCategoryTypes(task_id)

                            category_list = []
                            categorytype_list = []

                            for i in range(0, len(categories)):
                                category_list.append(categories[i][0].split())
                                categorytype_list.append(categorytype[i][0].split())

                            category_len = len(category_list)
                            categorysub_len = []
                            for j in range(0, category_len):
                                categorysub_len.append(len(category_list[j]))
                            try:
                                marked_category = get_single_database.getMarkedCategories(task_id, min_page)
                                marked_category_list = marked_category[0][0].split()
                                marked_category_len = len(marked_category_list)

                                marked_single_category = get_single_database.getMarkedSingleCategories(task_id,
                                                                                                       min_page)
                                marked_single_list = marked_single_category[0][0].split()
                                marked_single_len = len(marked_single_list)
                            except:
                                marked_category_list = []
                                marked_category_len = 0
                                marked_single_list = []
                                marked_single_len = 0
                                pass

                            return render_template('setcategorical.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, setlen=set_len, setlistlen=list_set_len,
                                                   imgset=list_imgid_set, imgsetlen=imgset_len, category=category_list,
                                                   categorytype=categorytype_list, categorylen=category_len,
                                                   categorysublen=categorysub_len, markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len,
                                                   maxduration=maxtime_js, remaining=remaining)

                        else:
                            return render_template('binaryset.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, setlen=set_len, setlistlen=list_set_len,
                                                   imgset=list_imgid_set, imgsetlen=imgset_len, maxduration=maxtime_js
                                                   ,remaining=remaining)
                    else:
                        if int(min_page) == max_page:
                            raiser = get_single_database.getRaiserName(task_id)
                            return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                                   taskid=task_id,
                                                   raiser=raiser, userid=user_id)
                        if int(min_page) > max_page:
                            raiser = get_single_database.getRaiserName(task_id)
                            return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                                   taskid=task_id,
                                                   raiser=raiser, user_id=user_id)
                        else:
                            return render_template('error.html')
                else:
                    get_single_database.setNoneRegister(task_id, user_id)
                    return render_template('expired.html')
            else:
                all_marked = request.get_json()
                return "ok"


        else:
            all_marked = request.get_json()
            img_id_mark = all_marked['marked']
            get_single_database.setNoneAnnotationResult(email, task_id, min_page)
            get_single_database.updateAnnotationResult(email, task_id, img_id_mark)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_single_database.setCategoryResult(task_id, min_page, checkboxes)
                get_single_database.setNoneSingleResult(task_id, min_page, "Na")
                get_single_database.setSingleResult(task_id, min_page, radioboxes)
            except:
                pass

            return "okay"
    except:
        return render_template('error.html')


# Tertiary Image

@app.route('/tertiary/<string:task_id>/<string:userid>/<string:req_type>/<string:min_page>', methods=['GET', 'POST'])
def do_tertiary(task_id, userid, req_type, min_page):
    try:
        global marked, all_marked, email
        marked = []
        all_marked = []
        get_single_database = DatabaseHelper()
        if request.method == 'GET':
            if req_type == "redirect":
                pages_per_annotator = get_single_database.getPagesPerAnnotator(task_id)
                user_id = userid
                email = get_single_database.getEmail(user_id)
                default = get_single_database.getDefaultclick(task_id)
                leftclick = get_single_database.getLeftclick(task_id)
                rightclick = get_single_database.getRightclick(task_id)
                categorical_task = get_single_database.getCategoryPosition(task_id)
                is_local = get_single_database.getLocal(task_id)

                try:
                    min_page_db = get_single_database.getFirstPage(task_id, email, user_id)
                    last_page_db = get_single_database.getLastPage(task_id)
                    max_duration = get_single_database.getMaxDuration(task_id)
                    max_page = int(min_page_db) + int(pages_per_annotator)
                    questions = get_single_database.getQuestions(task_id, email, min_page)
                    get_url_boto = BotoFramework()
                    if is_local == "true":
                        list_questions = []
                        for i in questions:
                            list_questions.append(i[0])
                        temp_url = list_questions
                    else:
                        temp_url = get_url_boto.getTempUrl(questions, max_duration)

                    title = get_single_database.getTitle(task_id)
                    instruction = get_single_database.getInstructions(task_id)
                    img_id = get_single_database.getImageid(task_id, email, min_page)
                    total_len = len(temp_url)

                    mark_id = get_single_database.getGreenMarkedImageid(task_id, email, min_page)
                    mark_len = len(mark_id)

                    red_mark_id = get_single_database.getRedMarkedImageid(task_id, email, min_page)
                    red_mark_len = len(red_mark_id)


                except:
                    max_page = int(pages_per_annotator)
                    pass

                max_time = get_single_database.getMaxTime(task_id, user_id)
                current_time = datetime.now()
                dt = datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f")
                dt_round_microsec = round(dt.microsecond / 1000000)
                dt = dt.replace(microsecond=dt_round_microsec)
                maxtime_js = datetime.strftime(dt, "%b %d, %Y %H:%M:%S")

                if current_time < datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f"):
                    if int(min_page) > max_page:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                               taskid=task_id,
                                               raiser=raiser, userid=user_id)

                    if int(min_page) == last_page_db + 1:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator, taskid=task_id,
                                               raiser=raiser, userid=user_id)
                    if int(min_page) < max_page:
                        remaining = max_page - int(min_page)
                        if categorical_task > 0:
                            categories = get_single_database.getCategories(task_id)
                            categorytype = get_single_database.getAllCategoryTypes(task_id)

                            category_list = []
                            categorytype_list = []

                            for i in range(0, len(categories)):
                                category_list.append(categories[i][0].split())
                                categorytype_list.append(categorytype[i][0].split())

                            category_len = len(category_list)
                            categorysub_len = []
                            for j in range(0, category_len):
                                categorysub_len.append(len(category_list[j]))
                            try:
                                marked_category = get_single_database.getMarkedCategories(task_id, min_page)
                                marked_category_list = marked_category[0][0].split()
                                marked_category_len = len(marked_category_list)

                                marked_single_category = get_single_database.getMarkedSingleCategories(task_id,
                                                                                                       min_page)
                                marked_single_list = marked_single_category[0][0].split()
                                marked_single_len = len(marked_single_list)
                            except:
                                marked_category_list = []
                                marked_category_len = 0
                                marked_single_list = []
                                marked_single_len = 0
                                pass

                            return render_template('tertiarycategorical.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, redmark=red_mark_id, redmarklen=red_mark_len,
                                                   default=default, leftclick=leftclick, rightclick=rightclick,
                                                   category=category_list,
                                                   categorytype=categorytype_list, categorylen=category_len,
                                                   categorysublen=categorysub_len, markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len,
                                                   maxduration=maxtime_js,remaining=remaining)

                        else:
                            return render_template('tertiarysingle.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, redmark=red_mark_id, redmarklen=red_mark_len,
                                                   default=default, leftclick=leftclick, rightclick=rightclick,  maxduration=maxtime_js,remaining=remaining)
                    else:
                        if int(min_page) == max_page:
                            raiser = get_single_database.getRaiserName(task_id)
                            return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                                   taskid=task_id,
                                                   raiser=raiser, userid=user_id)

                        else:
                            return render_template('error.html')
                else:
                    get_single_database.setNoneRegister(task_id, user_id)
                    return render_template('expired.html')
            else:
                all_marked = request.get_json()
                return "ok"


        else:
            email = get_single_database.getEmail(userid)
            all_marked = request.get_json()
            img_id_mark = all_marked['marked']
            img_id_mark_red = all_marked['redmarked']
            get_single_database.setNoneTertiaryAnnotationResult(email, task_id, min_page)
            get_single_database.updateGreenAnnotationResult(email, task_id, img_id_mark)
            get_single_database.updateRedAnnotationResult(email, task_id, img_id_mark_red)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_single_database.setCategoryResult(task_id, min_page, checkboxes)
                get_single_database.setNoneSingleResult(task_id, min_page, "Na")
                get_single_database.setSingleResult(task_id, min_page, radioboxes)
            except:
                pass

            return "okay"

    except:
        return render_template('error.html')




# Video

@app.route('/video/<string:task_id>/<string:userid>/<string:req_type>/<string:min_page>', methods=['GET', 'POST'])
def do_Video(task_id, userid, req_type, min_page):
    try:
        global marked, all_marked, email
        marked = []
        all_marked = []
        get_single_database = DatabaseHelper()
        if request.method == 'GET':
            if req_type == "redirect":
                pages_per_annotator = get_single_database.getPagesPerAnnotator(task_id)
                user_id = userid
                email = get_single_database.getEmail(user_id)
                is_local = get_single_database.getLocal(task_id)

                try:
                    min_page_db = get_single_database.getFirstPage(task_id, email, user_id)
                    last_page_db = get_single_database.getLastPage(task_id)
                    max_duration = get_single_database.getMaxDuration(task_id)
                    max_page = int(min_page_db) + int(pages_per_annotator)
                    questions = get_single_database.getQuestions(task_id, email, min_page)
                    get_url_boto = BotoFramework()
                    if is_local == "true":
                        list_questions = []
                        for i in questions:
                            list_questions.append(i[0])
                        temp_url = list_questions
                    else:
                        temp_url = get_url_boto.getTempUrl(questions, max_duration)

                    title = get_single_database.getTitle(task_id)
                    instruction = get_single_database.getInstructions(task_id)
                    img_id = get_single_database.getImageid(task_id, email, min_page)
                    total_len = len(temp_url)
                except:
                    max_page = int(pages_per_annotator)
                    pass

                max_time = get_single_database.getMaxTime(task_id, user_id)
                current_time = datetime.now()
                dt = datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f")
                dt_round_microsec = round(dt.microsecond / 1000000)
                dt = dt.replace(microsecond=dt_round_microsec)
                maxtime_js = datetime.strftime(dt, "%b %d, %Y %H:%M:%S")

                if current_time < datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S.%f"):
                    if int(min_page) > max_page:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                               taskid=task_id,
                                               raiser=raiser, userid=user_id)

                    if int(min_page) == last_page_db + 1:
                        raiser = get_single_database.getRaiserName(task_id)
                        return render_template('summary.html', email=email, tasks=pages_per_annotator, taskid=task_id,
                                               raiser=raiser, userid=user_id)
                    if int(min_page) < max_page:
                        remaining = max_page - int(min_page)
                        categories = get_single_database.getCategories(task_id)
                        categorytype = get_single_database.getAllCategoryTypes(task_id)

                        category_list = []
                        categorytype_list = []

                        for i in range(0, len(categories)):
                            category_list.append(categories[i][0].split())
                            categorytype_list.append(categorytype[i][0].split())

                        category_len = len(category_list)
                        categorysub_len = []
                        for j in range(0, category_len):
                            categorysub_len.append(len(category_list[j]))

                        try:
                            checker = get_single_database.getCountOneType(task_id)
                            marked_category = get_single_database.getMarkedCategories(task_id, min_page)
                            marked_category_list = marked_category[0][0].split()
                            marked_category_len = len(marked_category_list)

                            marked_single_category = get_single_database.getMarkedSingleCategories(task_id,
                                                                                                   min_page)
                            marked_single_list = marked_single_category[0][0].split()
                            marked_single_len = len(marked_single_list)
                        except:
                            marked_category_list = []
                            marked_category_len = 0
                            marked_single_list = []
                            marked_single_len = 0
                            pass

                        return render_template('videocategorical.html', questionset=temp_url,
                                               totallength=total_len, title=title, instruction=instruction,
                                               imgid=img_id, taskid=task_id, email=user_id, page=min_page,
                                               category=category_list,categorytype=categorytype_list,
                                               categorylen=category_len,categorysublen=categorysub_len,
                                               markedcategory=marked_category_list, markedcategorylen=marked_category_len,
                                               markedsingle=marked_single_list, markedsinglelen=marked_single_len,
                                               maxduration=maxtime_js, remaining=remaining, checker=checker)


                    else:
                        if int(min_page) == max_page:
                            raiser = get_single_database.getRaiserName(task_id)
                            return render_template('summary.html', email=email, tasks=pages_per_annotator,
                                                   taskid=task_id,
                                                   raiser=raiser, userid=user_id)

                        else:
                            return render_template('error.html')
                else:
                    get_single_database.setNoneRegister(task_id, user_id)
                    return render_template('expired.html')
            else:
                all_marked = request.get_json()
                return "ok"


        else:
            email = get_single_database.getEmail(userid)
            all_marked = request.get_json()
            get_single_database.updateVideoAnnotationResult(email, task_id, min_page)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_single_database.setCategoryResult(task_id, min_page, checkboxes)
                get_single_database.setNoneSingleResult(task_id, min_page, "Na")
                get_single_database.setSingleResult(task_id, min_page, radioboxes)
            except:
                pass
            return "okay"

    except Exception as e:
        return render_template('error.html')





# View Single

@app.route('/view/<string:task_id>/<string:min_page>', methods=['GET', 'POST'])
def do_view(task_id, min_page):
    try:
        get_view_database = DatabaseHelper()
        if request.method == 'GET':
            title = get_view_database.getTitle(task_id)
            instruction = get_view_database.getInstructions(task_id)
            max_page = get_view_database.getMaxPageNumber(task_id)
            max_duration = get_view_database.getMaxDuration(task_id)
            questions = get_view_database.getViewQuestions(task_id, min_page)
            categorical_task = get_view_database.getCategoryPosition(task_id)
            is_local = get_view_database.getLocal(task_id)

            img_id = get_view_database.getViewImageid(task_id, min_page)
            mark_id = get_view_database.getMarkedViewImageid(task_id, min_page)
            mark_len = len(mark_id)

            get_url_boto = BotoFramework()
            if is_local == "true":
                list_questions = []
                for i in questions:
                    list_questions.append(i[0])
                temp_url = list_questions
            else:
                temp_url = get_url_boto.getTempUrl(questions, max_duration)

            total_len = len(temp_url)
            if int(min_page) <= max_page:
                if categorical_task > 0:
                    categories = get_view_database.getCategories(task_id)
                    categorytype = get_view_database.getAllCategoryTypes(task_id)

                    category_list = []
                    categorytype_list = []

                    for i in range(0, len(categories)):
                        category_list.append(categories[i][0].split())
                        categorytype_list.append(categorytype[i][0].split())

                    category_len = len(category_list)
                    categorysub_len = []
                    for j in range(0, category_len):
                        categorysub_len.append(len(category_list[j]))

                    try:
                        marked_category = get_view_database.getMarkedCategories(task_id, min_page)
                        marked_category_list = marked_category[0][0].split()
                        marked_category_len = len(marked_category_list)

                        marked_single_category = get_view_database.getMarkedSingleCategories(task_id,
                                                                                               min_page)
                        marked_single_list = marked_single_category[0][0].split()
                        marked_single_len = len(marked_single_list)
                    except:
                        marked_category_list = []
                        marked_category_len = 0
                        marked_single_list = []
                        marked_single_len = 0
                        pass

                    return render_template('viewtestcategorical.html',questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, category=category_list,
                                                   categorytype=categorytype_list,
                                                   categorylen=category_len, categorysublen=categorysub_len,
                                                   markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len)
                else:
                    return render_template('viewtest.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id,  page=min_page,
                                                   mark=mark_id, marklen=mark_len)
            else:
                if int(min_page) == max_page + 1:
                    return render_template('viewsummary.html')
                else:
                    return render_template('error.html')

        else:

            all_marked = request.get_json()
            img_id_mark = all_marked['marked']
            get_view_database.setViewNoneAnnotationResult(task_id, min_page)
            get_view_database.updateViewAnnotationResult(task_id, img_id_mark)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_view_database.setCategoryResult(task_id, min_page, checkboxes)
                get_view_database.setNoneSingleResult(task_id, min_page, "Na")
                get_view_database.setSingleResult(task_id, min_page, radioboxes)

            except:
                pass

        return "okay"

    except Exception as e:
        print(e)
        return render_template('error.html')



#tertiary view

@app.route('/tertiaryview/<string:task_id>/<string:min_page>', methods=['GET', 'POST'])
def do_tertiaryview(task_id, min_page):
    try:
        get_view_database = DatabaseHelper()
        if request.method == 'GET':
            title = get_view_database.getTitle(task_id)
            instruction = get_view_database.getInstructions(task_id)
            max_page = get_view_database.getMaxPageNumber(task_id)
            max_duration = get_view_database.getMaxDuration(task_id)
            questions = get_view_database.getViewQuestions(task_id, min_page)
            categorical_task = get_view_database.getCategoryPosition(task_id)
            is_local = get_view_database.getLocal(task_id)
            default = get_view_database.getDefaultclick(task_id)
            leftclick = get_view_database.getLeftclick(task_id)
            rightclick = get_view_database.getRightclick(task_id)

            img_id = get_view_database.getViewImageid(task_id, min_page)
            mark_id = get_view_database.getViewGreenMarkedImageid(task_id, min_page)
            mark_len = len(mark_id)
            red_mark_id = get_view_database.getViewRedMarkedImageid(task_id, min_page)
            red_mark_len = len(red_mark_id)


            get_url_boto = BotoFramework()
            if is_local == "true":
                list_questions = []
                for i in questions:
                    list_questions.append(i[0])
                temp_url = list_questions
            else:
                temp_url = get_url_boto.getTempUrl(questions, max_duration)


            total_len = len(temp_url)
            if int(min_page) <= max_page:
                if categorical_task > 0:
                    categories = get_view_database.getCategories(task_id)
                    categorytype = get_view_database.getAllCategoryTypes(task_id)

                    category_list = []
                    categorytype_list = []

                    for i in range(0, len(categories)):
                        category_list.append(categories[i][0].split())
                        categorytype_list.append(categorytype[i][0].split())

                    category_len = len(category_list)
                    categorysub_len = []
                    for j in range(0, category_len):
                        categorysub_len.append(len(category_list[j]))

                    try:
                        checker = get_view_database.getCountOneType(task_id)
                        marked_category = get_view_database.getMarkedCategories(task_id, min_page)
                        marked_category_list = marked_category[0][0].split()
                        marked_category_len = len(marked_category_list)

                        marked_single_category = get_view_database.getMarkedSingleCategories(task_id,
                                                                                               min_page)
                        marked_single_list = marked_single_category[0][0].split()
                        marked_single_len = len(marked_single_list)
                    except:
                        marked_category_list = []
                        marked_category_len = 0
                        marked_single_list = []
                        marked_single_len = 0
                        pass

                    return render_template('viewtertiarycategorical.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, redmark=red_mark_id, redmarklen=red_mark_len,
                                                   default=default, leftclick=leftclick, rightclick=rightclick,
                                                   category=category_list,
                                                   categorytype=categorytype_list, categorylen=category_len,
                                                   categorysublen=categorysub_len, markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len, checker=checker)
                else:
                    return render_template('viewtertiary.html',questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, redmark=red_mark_id, redmarklen=red_mark_len,
                                                   default=default, leftclick=leftclick, rightclick=rightclick)
            else:
                if int(min_page) == max_page + 1:
                    return render_template('viewsummary.html')
                else:
                    return render_template('error.html')

        else:

            all_marked = request.get_json()
            img_id_mark = all_marked['marked']
            img_id_mark_red = all_marked['redmarked']
            get_view_database.setViewNoneTertiaryAnnotationResult(task_id, min_page)
            get_view_database.updateViewGreenAnnotationResult(task_id, img_id_mark)
            get_view_database.updateViewRedAnnotationResult(task_id, img_id_mark_red)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_view_database.setCategoryResult(task_id, min_page, checkboxes)
                get_view_database.setNoneSingleResult(task_id, min_page, "Na")
                get_view_database.setSingleResult(task_id, min_page, radioboxes)
            except:
                pass
            return "okay"

    except Exception as e:
        print(e)
        return render_template('error.html')


# View Set

@app.route('/binarysetview/<string:task_id>/<string:min_page>', methods=['GET', 'POST'])
def do_setview(task_id, min_page):
    try:
        global marked, all_marked
        marked = []
        all_marked = []

        get_single_database = DatabaseHelper()
        if request.method == 'GET':

            max_duration = get_single_database.getMaxDuration(task_id)
            max_page = get_single_database.getMaxPageNumber(task_id)
            questions = get_single_database.getViewQuestions(task_id, min_page)
            categorical_task = get_single_database.getCategoryPosition(task_id)
            is_local = get_single_database.getLocal(task_id)

            get_url_boto = BotoFramework()
            if is_local == "true":
                list_questions = []
                for i in questions:
                    list_questions.append(i[0])
                temp_url = list_questions
            else:
                temp_url = get_url_boto.getTempUrl(questions, max_duration)

            total_len = len(temp_url)

            max_set = get_single_database.getMaxSetView(task_id, min_page)
            min_set = get_single_database.getMinSetView(task_id, min_page)

            img_id = get_single_database.getViewImageid(task_id, min_page)
            mark_id = get_single_database.getMarkedViewImageid(task_id, min_page)
            mark_len = len(mark_id)

            try:
                set_len = get_single_database.getSetLengthView(task_id, max_set, min_set, min_page)
                list_set_len = len(set_len)

                imgid_set = get_single_database.getImgIdSetView(task_id, min_page, max_set, min_set)
                imgset_len = len(imgid_set)

                list_imgid_set = [[] for _ in range(imgset_len)]
                for i in range(0, imgset_len):
                    for j in range(0, len(imgid_set[i])):
                        list_imgid_set[i].append(imgid_set[i][j][0])
            except:
                list_set_len = 0
                list_imgid_set = [[]]
                imgset_len = []
                pass

            title = get_single_database.getTitle(task_id)
            instruction = get_single_database.getInstructions(task_id)

            if int(min_page) <= max_page:
                if categorical_task > 0:
                    categories = get_single_database.getCategories(task_id)
                    categorytype = get_single_database.getAllCategoryTypes(task_id)

                    category_list = []
                    categorytype_list = []

                    for i in range(0, len(categories)):
                        category_list.append(categories[i][0].split())
                        categorytype_list.append(categorytype[i][0].split())

                    category_len = len(category_list)
                    categorysub_len = []
                    for j in range(0, category_len):
                        categorysub_len.append(len(category_list[j]))

                    try:
                        marked_category = get_single_database.getMarkedCategories(task_id, min_page)
                        marked_category_list = marked_category[0][0].split()
                        marked_category_len = len(marked_category_list)

                        marked_single_category = get_single_database.getMarkedSingleCategories(task_id,
                                                                                               min_page)
                        marked_single_list = marked_single_category[0][0].split()
                        marked_single_len = len(marked_single_list)
                    except:
                        marked_category_list = []
                        marked_category_len = 0
                        marked_single_list = []
                        marked_single_len = 0
                        pass

                    return render_template('binarysetviewcategorical.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, setlen=set_len, setlistlen=list_set_len,
                                                   imgset=list_imgid_set, imgsetlen=imgset_len, category=category_list,
                                                   categorytype=categorytype_list, categorylen=category_len,
                                                   categorysublen=categorysub_len, markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len)
                else:

                    return render_template('binarysetview.html',questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, page=min_page,
                                                   mark=mark_id,
                                                   marklen=mark_len, setlen=set_len, setlistlen=list_set_len,
                                                   imgset=list_imgid_set, imgsetlen=imgset_len)
            else:
                if int(min_page) == max_page + 1:
                    return render_template('viewsummary.html')
                else:
                    return render_template('error.html')
        else:
            all_marked = request.get_json()
            img_id_mark = all_marked['marked']
            get_single_database.setViewNoneAnnotationResult(task_id, min_page)
            get_single_database.updateViewAnnotationResult(task_id, img_id_mark)
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_single_database.setCategoryResult(task_id, min_page, checkboxes)
                get_single_database.setNoneSingleResult(task_id, min_page, "Na")
                get_single_database.setSingleResult(task_id, min_page, radioboxes)
            except:
                pass
            return "okay"



    except Exception as e:
        print(e)
        return render_template('error.html')


# Video View

@app.route('/videoview/<string:task_id>/<string:min_page>', methods=['GET', 'POST'])
def do_videoview(task_id, min_page):
    try:
        get_view_database = DatabaseHelper()
        if request.method == 'GET':
            title = get_view_database.getTitle(task_id)
            instruction = get_view_database.getInstructions(task_id)
            max_page = get_view_database.getMaxPageNumber(task_id)
            max_duration = get_view_database.getMaxDuration(task_id)
            questions = get_view_database.getViewQuestions(task_id, min_page)

            is_local = get_view_database.getLocal(task_id)
            img_id = get_view_database.getViewImageid(task_id, min_page)


            get_url_boto = BotoFramework()
            if is_local == "true":
                list_questions = []
                for i in questions:
                    list_questions.append(i[0])
                temp_url = list_questions
            else:
                temp_url = get_url_boto.getTempUrl(questions, max_duration)


            total_len = len(temp_url)
            if int(min_page) <= max_page:

                    categories = get_view_database.getCategories(task_id)
                    categorytype = get_view_database.getAllCategoryTypes(task_id)

                    category_list = []
                    categorytype_list = []

                    for i in range(0, len(categories)):
                        category_list.append(categories[i][0].split())
                        categorytype_list.append(categorytype[i][0].split())

                    category_len = len(category_list)
                    categorysub_len = []
                    for j in range(0, category_len):
                        categorysub_len.append(len(category_list[j]))

                    try:
                        marked_category = get_view_database.getMarkedCategories(task_id, min_page)
                        marked_category_list = marked_category[0][0].split()
                        marked_category_len = len(marked_category_list)

                        marked_single_category = get_view_database.getMarkedSingleCategories(task_id,
                                                                                               min_page)
                        marked_single_list = marked_single_category[0][0].split()
                        marked_single_len = len(marked_single_list)
                    except:
                        marked_category_list = []
                        marked_category_len = 0
                        marked_single_list = []
                        marked_single_len = 0
                        pass

                    return render_template('viewvideocategorical.html', questionset=temp_url,
                                                   totallength=total_len, title=title, instruction=instruction,
                                                   imgid=img_id, taskid=task_id, page=min_page,
                                                   category=category_list,
                                                   categorytype=categorytype_list, categorylen=category_len,
                                                   categorysublen=categorysub_len, markedcategory=marked_category_list,
                                                   markedcategorylen=marked_category_len,
                                                   markedsingle=marked_single_list, markedsinglelen=marked_single_len)

            else:
                if int(min_page) == max_page + 1:
                    return render_template('viewsummary.html')
                else:
                    return render_template('error.html')

        else:

            all_marked = request.get_json()
            try:
                checkboxes = all_marked['selectedBoxes']
                radioboxes = all_marked['radioselectedBoxes']
                get_view_database.setCategoryResult(task_id, min_page, checkboxes)
                get_view_database.setNoneSingleResult(task_id, min_page, "Na")
                get_view_database.setSingleResult(task_id, min_page, radioboxes)

            except:
                pass
            return "okay"

    except Exception as e:
        print(e)
        return render_template('error.html')








# Generate CSV


@app.route('/generate/<string:task_id>', methods=['GET'])
def do_generate(task_id):
    try:
        get_results_db = DatabaseHelper()
        task_type = get_results_db.getTaskType(task_id)
        categorical_task = get_results_db.getCategoryPosition(task_id)

        if categorical_task > 0:
            result = get_results_db.getResults(task_id)
            total_categories = get_results_db.getTotalMultipleCategories(task_id)
            selected_results = get_results_db.getResultsCategorical(task_id)
            csv_gen = CsvGenerator()

            single_results = get_results_db.getResultsSingleCategorical(task_id)
            single_headers = get_results_db.getResultsHeaderSingleCategorical(task_id)
            if single_results != None:
                file_creation = csv_gen.downloadCategoricalSingleCsv(result, "categorical", total_categories,
                                                                     selected_results, single_results, single_headers)
            else:
                file_creation = csv_gen.downloadCategoricalCsv(result, "categorical", total_categories,
                                                               selected_results)

            if file_creation:
                return send_file('csvfile.csv', as_attachment=True)
            else:
                return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

        else:
            if task_type == "binary":
                result = get_results_db.getResults(task_id)
                names = get_results_db.getNames(task_id)
                csv_gen = CsvGenerator()
                file_creation = csv_gen.downloadCsv(result, "binary", names)
                if file_creation:
                    return send_file('csvfile.csv', as_attachment=True)
                else:
                    return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

            if task_type == "binaryset":
                result = get_results_db.getResultsSet(task_id)
                names = get_results_db.getNames(task_id)
                csv_gen = CsvGenerator()
                file_creation = csv_gen.downloadCsv(result, "binaryset", names)
                if file_creation:
                    return send_file('csvfile.csv', as_attachment=True)
                else:
                    return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

            if task_type == "tertiary":
                result = get_results_db.getResults(task_id)
                names = get_results_db.getNames(task_id)
                csv_gen = CsvGenerator()
                file_creation = csv_gen.downloadCsv(result, "binary", names)
                if file_creation:
                    return send_file('csvfile.csv', as_attachment=True)
                else:
                    return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

    except:
        return render_template('error.html')


# generate now

@app.route('/generatenow/<string:task_id>', methods=['GET'])
def do_generatenow(task_id):
    try:
        get_results_db = DatabaseHelper()
        task_type = get_results_db.getTaskType(task_id)
        categorical_task = get_results_db.getCategoryPosition(task_id)

        if categorical_task > 0:
            result = get_results_db.getGenerateNowResults(task_id)
            total_categories = get_results_db.getTotalMultipleCategories(task_id)
            selected_results = get_results_db.getResultsCategorical(task_id)
            csv_gen = CsvGenerator()

            single_results = get_results_db.getResultsSingleCategorical(task_id)
            single_headers = get_results_db.getResultsHeaderSingleCategorical(task_id)
            if single_results != None:
                file_creation = csv_gen.downloadCategoricalSingleCsv(result, "categorical", total_categories,
                                                                     selected_results, single_results, single_headers)
            else:
                file_creation = csv_gen.downloadCategoricalCsv(result, "categorical", total_categories,
                                                               selected_results)

            if file_creation:
                return send_file('csvfile.csv', as_attachment=True)
            else:
                return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

        else:
            if task_type == "binary":
                result = get_results_db.getGenerateNowResults(task_id)
                names = get_results_db.getNames(task_id)
                csv_gen = CsvGenerator()
                file_creation = csv_gen.downloadCsv(result, "binary", names)
                if file_creation:
                    return send_file('csvfile.csv', as_attachment=True)
                else:
                    return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

            if task_type == "binaryset":
                result = get_results_db.getResultsSet(task_id)
                names = get_results_db.getNames(task_id)
                csv_gen = CsvGenerator()
                file_creation = csv_gen.downloadCsv(result, "binaryset", names)
                if file_creation:
                    return send_file('csvfile.csv', as_attachment=True)
                else:
                    return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})

            if task_type == "tertiary":
                result = get_results_db.getResults(task_id)
                names = get_results_db.getNames(task_id)
                csv_gen = CsvGenerator()
                file_creation = csv_gen.downloadCsv(result, "binary", names)
                if file_creation:
                    return send_file('csvfile.csv', as_attachment=True)
                else:
                    return jsonify({"download": "failed! report: avasudevan@sensoryinc.com"})



    except:
        return render_template('error.html')


# Logout


@app.route('/logout/<string:task_id>/<string:email>/<string:userid>')
def do_logout(task_id, email, userid):
    try:
        set_results = DatabaseHelper()
        task_type = set_results.getTaskType(task_id)
        if task_type == "tertiary":
            set_results.updateAllTertiaryAnnotationResult(email, task_id, userid)
            check_autoroutine = AutoRoutine()
            check_autoroutine.checkStatus(task_id)
            return render_template('logout.html')
        else:
            set_results.updateAllAnnotationResult(email, task_id, userid)
            set_results.updateAllAnnotationTrueResult(email, task_id, userid)
            check_autoroutine = AutoRoutine()
            check_autoroutine.checkStatus(task_id)
        return render_template('logout.html')

    except:
        return render_template('error.html')


# Summary


@app.route('/summary')
def do_summary():
    return render_template('summary.html')


@app.route('/logout')
def do_logoutview():
    return "Logout confirmed"


if __name__ == '__main__':
    app.run(debug=True)
