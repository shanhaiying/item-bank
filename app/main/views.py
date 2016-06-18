# -*- coding: utf-8 -*-

import os
import re
import json
import random
import urllib
import datetime

from app.main import main
from flask import render_template, redirect, url_for, request, current_app, \
        make_response, flash
from flask.ext.login import login_required, current_user
from app.models import SingleChoice, BlankFill, Essay, Points, Subject, TestPaper
from forms import SingleChoiceForm, BlankFillForm, EssayForm, DeleteForm, \
        TestPaperConstraintForm, PointForm, SubjectForm, TestPaperReplaceForm, \
        TestPaperNameForm
from app import db

from genetic_algorithm.db import DB
from genetic_algorithm.paper import Paper
from genetic_algorithm.problem import Problem
from genetic_algorithm.main import Genetic

@main.route('/')
def index_or_login():
    if current_user.is_authenticated():
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('auth.login'))

@main.route('/index')
@login_required
def index():
    return render_template('index.html')

@main.route('/single_choice', methods=['GET', 'POST'])
@login_required
def single_choice():
    form = SingleChoiceForm()
    form.knowledge_points.choices = \
            [(p.id, p.name) for p in Points.query.all()]
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        p = Points.query.filter_by(id=form.knowledge_points.data).first()
        if p.subject != form.subject.data:
            flash(u'知识点与课程不符')
            return redirect(url_for('main.single_choice'))
        if form.A.data[:3] == "<p>":
            form.A.data = form.A.data[3:-6]
        if form.B.data[:3] == "<p>":
            form.B.data = form.B.data[3:-6]
        if form.C.data[:3] == "<p>":
            form.C.data = form.C.data[3:-6]
        if form.D.data[:3] == "<p>":
            form.D.data = form.D.data[3:-6]
        single_choice = SingleChoice(question=form.question.data,
                difficult_level=form.difficult_level.data,
                faq=form.faq.data, A=form.A.data,
                B=form.B.data, C=form.C.data, D=form.D.data,
                knowledge_points=form.knowledge_points.data,
                subject=form.subject.data,
                answer=form.answer.data)

        p = Points.query.filter_by(id=single_choice.knowledge_points).first()
        single_choice.knowledge_points_name = p.name
        s = Subject.query.filter_by(id=single_choice.subject).first()
        single_choice.subject_name = s.name

        db.session.add(single_choice)
        db.session.commit()
        return redirect(url_for('main.single_choice'))
    page = request.args.get('page', 1, type=int)
    pagination = SingleChoice.query.order_by(
            SingleChoice.timestamp.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    single_choice = pagination.items
    return render_template('single_choice.html', form=form,
            single_choice=single_choice, pagination=pagination)

@main.route('/edit_single_choice/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_single_choice(id):
    single_choice = SingleChoice.query.get_or_404(id)
    form = SingleChoiceForm()
    form.knowledge_points.choices = [(p.id, p.name) for p in Points.query.all()]
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        p = Points.query.filter_by(id=form.knowledge_points.data).first()
        if p.subject != form.subject.data:
            flash(u'知识点与课程不符')
            return redirect(url_for('main.single_choice'))
        if form.A.data[:3] == "<p>":
            form.A.data = form.A.data[3:-6]
        if form.B.data[:3] == "<p>":
            form.B.data = form.B.data[3:-6]
        if form.C.data[:3] == "<p>":
            form.C.data = form.C.data[3:-6]
        if form.D.data[:3] == "<p>":
            form.D.data = form.D.data[3:-6]
        single_choice.question = form.question.data
        single_choice.difficult_level = form.difficult_level.data
        single_choice.faq = form.faq.data
        single_choice.A = form.A.data
        single_choice.B = form.B.data
        single_choice.C = form.C.data
        single_choice.D = form.D.data
        single_choice.knowledge_points = form.knowledge_points.data
        single_choice.subject = form.subject.data,
        single_choice.answer = form.answer.data
        p = Points.query.filter_by(id=single_choice.knowledge_points).first()
        single_choice.knowledge_points_name = p.name
        s = Subject.query.filter_by(id=single_choice.subject).first()
        single_choice.subject_name = s.name

        db.session.add(single_choice)
        db.session.commit()
        return redirect(url_for('main.single_choice'))

    form.question.data = single_choice.question
    form.difficult_level.data = single_choice.difficult_level
    form.faq.data = single_choice.faq
    form.A.data = single_choice.A
    form.B.data = single_choice.B
    form.C.data = single_choice.C
    form.D.data = single_choice.D
    form.knowledge_points.data = single_choice.knowledge_points
    form.subject.data = single_choice.subject
    form.answer.data = single_choice.answer
    return render_template('edit_single_choice.html', form=form)

@main.route('/delete_single_choice/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_single_choice(id):
    single_choice = SingleChoice.query.get_or_404(id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(single_choice)
        db.session.commit()
        return redirect(url_for('main.single_choice'))
    return render_template('delete_single_choice.html', form=form)

@main.route('/blank_fill', methods=['GET', 'POST'])
@login_required
def blank_fill():
    form = BlankFillForm()
    form.knowledge_points.choices = [(p.id, p.name) for p in Points.query.all()]
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        p = Points.query.filter_by(id=form.knowledge_points.data).first()
        if p.subject != form.subject.data:
            flash(u'知识点与课程不符')
            return redirect(url_for('main.blank_fill'))
        blank_fill = BlankFill(question=form.question.data,
                difficult_level=form.difficult_level.data,
                faq=form.faq.data,
                knowledge_points=form.knowledge_points.data,
                subject=form.subject.data,
                answer=form.answer.data)

        p = Points.query.filter_by(id=blank_fill.knowledge_points).first()
        blank_fill.knowledge_points_name = p.name
        s = Subject.query.filter_by(id=blank_fill.subject).first()
        blank_fill.subject_name = s.name

        db.session.add(blank_fill)
        db.session.commit()
        return redirect(url_for('main.blank_fill'))
    page = request.args.get('page', 1, type=int)
    pagination = BlankFill.query.order_by(
            BlankFill.timestamp.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    blank_fill = pagination.items
    return render_template('blank_fill.html', form=form,
            blank_fill=blank_fill, pagination=pagination)

@main.route('/edit_blank_fill/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blank_fill(id):
    blank_fill = BlankFill.query.get_or_404(id)
    form = BlankFillForm()
    form.knowledge_points.choices = [(p.id, p.name) for p in Points.query.all()]
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        p = Points.query.filter_by(id=form.knowledge_points.data).first()
        if p.subject != form.subject.data:
            flash(u'知识点与课程不符')
            return redirect(url_for('main.blank_fill'))
        blank_fill.question = form.question.data
        blank_fill.difficult_level = form.difficult_level.data
        blank_fill.faq = form.faq.data
        blank_fill.knowledge_points = form.knowledge_points.data
        blank_fill.subject = form.subject.data
        blank_fill.answer = form.answer.data

        p = Points.query.filter_by(id=blank_fill.knowledge_points).first()
        blank_fill.knowledge_points_name = p.name
        s = Subject.query.filter_by(id=blank_fill.subject).first()
        blank_fill.subject_name = s.name

        db.session.add(blank_fill)
        db.session.commit()
        return redirect(url_for('main.blank_fill'))

    form.question.data = blank_fill.question
    form.difficult_level.data = blank_fill.difficult_level
    form.faq.data = blank_fill.faq
    form.knowledge_points.data = blank_fill.knowledge_points
    form.subject.data = blank_fill.subject
    form.answer.data = blank_fill.answer
    return render_template('edit_blank_fill.html', form=form)

@main.route('/delete_blank_fill/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_blank_fill(id):
    blank_fill = BlankFill.query.get_or_404(id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(blank_fill)
        db.session.commit()
        return redirect(url_for('main.blank_fill'))
    return render_template('delete_blank_fill.html', form=form)

@main.route('/essay', methods=['GET', 'POST'])
@login_required
def essay():
    form = EssayForm()
    form.knowledge_points.choices = [(p.id, p.name) for p in Points.query.all()]
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        p = Points.query.filter_by(id=form.knowledge_points.data).first()
        if p.subject != form.subject.data:
            flash(u'知识点与课程不符')
            return redirect(url_for('main.essay'))
        essay = Essay(question=form.question.data,
                difficult_level=form.difficult_level.data,
                faq=form.faq.data,
                knowledge_points=form.knowledge_points.data,
                subject=form.subject.data,
                answer=form.answer.data)

        p = Points.query.filter_by(id=essay.knowledge_points).first()
        essay.knowledge_points_name = p.name
        s = Subject.query.filter_by(id=essay.subject).first()
        essay.subject_name = s.name

        db.session.add(essay)
        db.session.commit()
        return redirect(url_for('main.essay'))
    page = request.args.get('page', 1, type=int)
    pagination = Essay.query.order_by(
            Essay.timestamp.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    essay = pagination.items
    return render_template('essay.html', form=form,
            essay=essay, pagination=pagination)

@main.route('/edit_essay/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_essay(id):
    essay = Essay.query.get_or_404(id)
    form = EssayForm()
    form.knowledge_points.choices = [(p.id, p.name) for p in Points.query.all()]
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        p = Points.query.filter_by(id=form.knowledge_points.data).first()
        if p.subject != form.subject.data:
            flash(u'知识点与课程不符')
            return redirect(url_for('main.essay'))
        essay.question = form.question.data
        essay.difficult_level = form.difficult_level.data
        essay.faq = form.faq.data
        essay.knowledge_points = form.knowledge_points.data
        essay.subject = form.subject.data
        essay.answer = form.answer.data

        p = Points.query.filter_by(id=essay.knowledge_points).first()
        essay.knowledge_points_name = p.name
        s = Subject.query.filter_by(id=essay.subject).first()
        essay.subject_name = s.name

        db.session.add(essay)
        db.session.commit()
        return redirect(url_for('main.essay'))

    form.question.data = essay.question
    form.difficult_level.data = essay.difficult_level
    form.faq.data = essay.faq
    form.knowledge_points.data = essay.knowledge_points
    form.subject.data = essay.subject
    form.answer.data = essay.answer
    return render_template('edit_essay.html', form=form)

@main.route('/delete_essay/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_essay(id):
    essay = Essay.query.get_or_404(id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(essay)
        db.session.commit()
        return redirect(url_for('main.essay'))
    return render_template('delete_essay.html', form=form)

@main.route('/about')
@login_required
def about():
    return render_template('about.html')

@main.route('/manage/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def manage(subject_id):
    subject = Subject.query.all()
    if subject_id == 0:
        Points_query = Points.query
    else:
        Points_query = Points.query.filter_by(subject=subject_id)

    points = Points_query.all()

    point_form = PointForm()
    subject_form = SubjectForm()
    point_form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if point_form.validate_on_submit():
        s = Subject.query.filter_by(id=point_form.subject.data).first()
        point = Points(name=point_form.name.data,
                subject=point_form.subject.data, subject_name=s.name)
        db.session.add(point)
        db.session.commit()
        return redirect(url_for('main.manage', subject_id=point.subject))

    if subject_form.validate_on_submit():
        subject = Subject(name=subject_form.name.data)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for('main.manage', subject_id=0))

    return render_template('manage.html', points=points, subject=subject,
            point_form=point_form, subject_form=subject_form)

@main.route('/delete_subject/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(subject)
        db.session.commit()
        return redirect(url_for('main.manage', subject_id=0))
    return render_template('delete_subject.html', form=form)

@main.route('/edit_point/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_point(id):
    point = Points.query.get_or_404(id)
    form = PointForm()
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        point.name = form.name.data
        point.subject = form.subject.data
        s = Subject.query.filter_by(id=point.subject).first()
        point.subject_name = s.name
        sc = SingleChoice.query.filter_by(knowledge_points=point.id).all()
        for i in range(len(sc)):
            if sc[i].subject == point.subject:
                sc[i].knowledge_points_name = point.name
            else:
                sc[i].knowledge_points = 0
                sc[i].knowledge_points_name = ""
            db.session.add(sc[i])
        bf = BlankFill.query.filter_by(knowledge_points=point.id).all()
        for i in range(len(bf)):
            if bf[i].subject == point.subject:
                bf[i].knowledge_points_name = point.name
            else:
                bf[i].knowledge_points = 0
                bf[i].knowledge_points_name = ""
            db.session.add(bf[i])
        es = Essay.query.filter_by(knowledge_points=point.id).all()
        for i in range(len(es)):
            if es[i].subject == point.subject:
                es[i].knowledge_points_name = point.name
            else:
                es[i].knowledge_points = 0
                es[i].knowledge_points_name = ""
            db.session.add(es[i])
        db.session.add(point)
        db.session.commit()
        return redirect(url_for('main.manage', subject_id=point.subject))

    form.name.data = point.name
    form.subject.data = point.subject
    return render_template('edit_point.html', form=form)

@main.route('/delete_point/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_point(id):
    point = Points.query.get_or_404(id)
    form = DeleteForm()
    if form.validate_on_submit():
        sc = SingleChoice.query.filter_by(knowledge_points=point.id).all()
        for i in range(len(sc)):
            sc[i].knowledge_points = 0
            sc[i].knowledge_points_name = ""
            db.session.add(sc[i])
        bf = BlankFill.query.filter_by(knowledge_points=point.id).all()
        for i in range(len(bf)):
            bf[i].knowledge_points = 0
            bf[i].knowledge_points_name = ""
            db.session.add(bf[i])
        es = Essay.query.filter_by(knowledge_points=point.id).all()
        for i in range(len(es)):
            es[i].knowledge_points = 0
            es[i].knowledge_points_name = ""
            db.session.add(es[i])
        db.session.delete(point)
        db.session.commit()
        return redirect(url_for('main.manage', subject_id=point.subject))
    return render_template('delete_point.html', form=form)

def handle_str(problems):
    problems = problems[1:]
    problems = problems[:-1]
    ids = problems.split(', ')
    for i in range(len(ids)):
        ids[i] = long(ids[i])
    return ids

@main.route('/test_papers')
@login_required
def test_papers():
    page = request.args.get('page', 1, type=int)
    pagination = TestPaper.query.order_by(
            TestPaper.timestamp.desc()).paginate(
            page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
            error_out=False)
    test_papers = pagination.items
    return render_template('test_papers.html',
            test_papers=test_papers, pagination=pagination)

@main.route('/test_paper/<int:id>')
@login_required
def test_paper(id):
    test_paper = TestPaper.query.get_or_404(id)
    sc = handle_str(test_paper.single_choice)
    bf = handle_str(test_paper.blank_fill)
    es = handle_str(test_paper.essay)
    name = test_paper.name
    single_choice = []
    blank_fill = []
    essay = []
    for sc_id in sc:
        item = SingleChoice.query.filter_by(id=sc_id).first()
        single_choice.append(item)
    for bf_id in bf:
        item = BlankFill.query.filter_by(id=bf_id).first()
        blank_fill.append(item)
    for es_id in es:
        item = Essay.query.filter_by(id=es_id).first()
        essay.append(item)
    return render_template('test_paper.html',
            tp_id = test_paper.id,
            name = name,
            single_choice=single_choice,
            blank_fill=blank_fill,
            essay=essay)

@main.route('/edit_test_paper_name/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_test_paper_name(id):
    form = TestPaperNameForm()
    if form.validate_on_submit():
        test_paper = TestPaper.query.filter_by(id=id).first()
        test_paper.name = form.name.data
        db.session.add(test_paper)
        db.session.commit()
        return redirect(url_for('main.test_paper', id=id))
    return render_template('edit_test_paper.html', form=form)

@main.route('/edit_test_paper_sc/<int:tp_id>.<int:id>', methods=['GET', 'POST'])
@login_required
def edit_test_paper_sc(tp_id, id):
    form = TestPaperReplaceForm()
    if form.validate_on_submit():
        new_id = form.new_id.data
        test_paper = TestPaper.query.filter_by(id=tp_id).first()
        p = handle_str(test_paper.single_choice)
        for i in range(len(p)):
            if p[i] == new_id:
                flash(u'试题重复')
                return redirect(url_for('main.test_paper', id=tp_id))

        for i in range(len(p)):
            if p[i] == id:
                p[i] = new_id
        p_str = u'['
        p_str += u', '.join(unicode(e) for e in p)
        p_str += u']'
        test_paper.single_choice = p_str
        db.session.add(test_paper)
        db.session.commit()
        return redirect(url_for('main.test_paper', id=tp_id))
    return render_template('edit_test_paper.html', form=form)

@main.route('/edit_test_paper_bf/<int:tp_id>.<int:id>', methods=['GET', 'POST'])
@login_required
def edit_test_paper_bf(tp_id, id):
    form = TestPaperReplaceForm()
    if form.validate_on_submit():
        new_id = form.new_id.data
        test_paper = TestPaper.query.filter_by(id=tp_id).first()
        p = handle_str(test_paper.blank_fill)
        for i in range(len(p)):
            if p[i] == id:
                p[i] = new_id
        p_str = u'['
        p_str += u', '.join(unicode(e) for e in p)
        p_str += u']'
        test_paper.blank_fill = p_str
        db.session.add(test_paper)
        db.session.commit()
        return redirect(url_for('main.test_paper', id=tp_id))
    return render_template('edit_test_paper.html', form=form)

@main.route('/edit_test_paper_es/<int:tp_id>.<int:id>', methods=['GET', 'POST'])
@login_required
def edit_test_paper_es(tp_id, id):
    form = TestPaperReplaceForm()
    if form.validate_on_submit():
        new_id = form.new_id.data
        test_paper = TestPaper.query.filter_by(id=tp_id).first()
        p = handle_str(test_paper.essay)
        for i in range(len(p)):
            if p[i] == id:
                p[i] = new_id
        p_str = u'['
        p_str += u', '.join(unicode(e) for e in p)
        p_str += u']'
        test_paper.essay = p_str
        db.session.add(test_paper)
        db.session.commit()
        return redirect(url_for('main.test_paper', id=tp_id))
    return render_template('edit_test_paper.html', form=form)

@main.route('/delete_test_paper/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_test_paper(id):
    test_paper = TestPaper.query.get_or_404(id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(test_paper)
        db.session.commit()
        return redirect(url_for('main.test_papers'))
    return render_template('delete_test_paper.html', form=form)

@main.route('/new_test_paper/<name>.<subject>.<float:difficulty>.<sc>.<bf>.<es>',
        methods=['POST', 'GET'])
@login_required
def new_test_paper(name, subject, difficulty, sc, bf, es):
    sub = Subject.query.filter_by(id=subject).first()
    subject_name = sub.name
    test_paper = TestPaper(name=name, subject=subject,
            subject_name=subject_name,
            single_choice=sc, blank_fill=bf, essay=es)
    db.session.add(test_paper)
    db.session.commit()
    return render_template('index.html')

@main.route('/generate_test_paper', methods=['GET', 'POST'])
@login_required
def generate_test_paper():
    single_choice = []
    blank_fill = []
    essay = []
    sc_ids = []
    bf_ids = []
    es_ids = []
    each_point_score = []
    form = TestPaperConstraintForm()
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        name = form.name.data
        subject = form.subject.data
        single_choice_number = form.single_choice_number.data
        single_choice_score = form.single_choice_score.data
        blank_fill_number = form.blank_fill_number.data
        blank_fill_score = form.blank_fill_score.data
        essay_number = form.essay_number.data
        essay_score = form.essay_score.data
        difficulty = form.difficulty.data
        points = form.points.data
        each_point_score = form.each_point_score.data

        paper = Paper()
        paper.id = 1
        paper.difficulty = difficulty
        for p in points:
            pp = Points.query.filter_by(name=p).first()
            paper.points.append(pp.id)
        for eps in each_point_score:
            paper.each_point_score.append(int(eps))
        paper.each_type_count = [single_choice_number,
                blank_fill_number, essay_number]
        paper.each_type_score = [single_choice_score,
                blank_fill_score, essay_score]
        paper.total_score = single_choice_score + blank_fill_score + \
                essay_score

        single_choice = SingleChoice.query.filter_by(subject=subject).all()
        blank_fill = BlankFill.query.filter_by(subject=subject).all()
        essay = Essay.query.filter_by(subject=subject).all()

        problem_list = []
        for sc in single_choice:
            p = Problem()
            p.id = sc.id
            p.type = 1
            p.difficulty = sc.difficult_level
            p.points.append(sc.knowledge_points)
            p.score = single_choice_score / single_choice_number
            problem_list.append(p)

        for bf in blank_fill:
            p = Problem()
            p.id = bf.id
            p.type = 2
            p.difficulty = bf.difficult_level
            p.points.append(bf.knowledge_points)
            p.score = blank_fill_score / blank_fill_number
            problem_list.append(p)

        for es in essay:
            p = Problem()
            p.id = es.id
            p.type = 3
            p.difficulty = es.difficult_level
            p.points.append(es.knowledge_points)
            p.score = essay_score / essay_number
            problem_list.append(p)

        db = DB()
        db.create_from_problem_list(problem_list)
        genetic = Genetic(paper, db)
        u = genetic.run(0.98)

        single_choice = []
        blank_fill = []
        essay = []
        for p in u.problem_list:
            if p.type == 1:
                sc = SingleChoice.query.filter_by(id=p.id).all()
                single_choice += sc
                for item in sc:
                    sc_ids.append(item.id)
            if p.type == 2:
                bf = BlankFill.query.filter_by(id=p.id).all()
                blank_fill += bf
                for item in bf:
                    bf_ids.append(item.id)
            if p.type == 3:
                es = Essay.query.filter_by(id=p.id).all()
                essay += es
                for item in es:
                    es_ids.append(item.id)

        return render_template('new_test_paper.html',
                name=name,
                single_choice=single_choice,
                blank_fill=blank_fill,
                essay=essay,
                sc_ids=sc_ids,
                bf_ids=bf_ids,
                es_ids=es_ids,
                subject=subject,
                difficulty=difficulty)
    return render_template('generate_test_paper.html', form=form)

def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@main.route('/ckupload/', methods=['POST', 'OPTIONS'])
@login_required
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'upload', rnd_name)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """<script type="text/javascript"> 
             window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
             </script>""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response
