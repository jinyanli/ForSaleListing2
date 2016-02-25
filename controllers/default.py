# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    #session.flash = T(request.args(0))
    unsold = request.args(0) == 'unsold'

    if  unsold:
        #session.flash = ("See All")
        forsale=(db.forsale.sold==False)
        button = A('See all', _class='btn btn-success', _href=URL('default', 'index'))
    else:
        #session.flash = ("Show  Unsold")
        forsale=db.forsale
        button = A('See Unsold', _class='btn btn-warning', _href=URL('default', 'index', args='unsold'))

    def generate_del_button(row):
        # only the author can delete it. Got this code from Luca's homework example
        b = ''
        if auth.user_id == row.user_id:
            b = A('Delete', _class='btn btn-danger', _href=URL('default', 'delete', args=[row.id],
                user_signature=True))
        return b

    def generate_edit_button(row):
        # only the author can edit it.
        b = ''
        if auth.user_id == row.user_id:
            b = A('Edit', _class='btn btn-danger', _href=URL('default', 'edit', args=[row.id]))
        return b

    def generate_view_button(row):
        b = A('view', _class='btn btn-primary', _href=URL('default', 'view', args=[row.id]))
        return b

    def generate_toggle_sold_button(row):
        # only the author can toggle it.
        b = ''
        if auth.user_id == row.user_id:
            if row.sold:
                name='Toggle Unsold'
            else:
                name='Toggle Sold'
            b = A(name, _class='btn btn-primary', _href=URL('default',
                  'toggle_sold', args=[row.id], user_signature=True))
        return b
    links = [
        dict(header='Delete', body = generate_del_button),
        dict(header='Edit', body = generate_edit_button),
        dict(header='Toggle Sold', body = generate_toggle_sold_button),
        dict(header='View', body = generate_view_button)
        ]

    grid = SQLFORM.grid(forsale, csv=False, create=False, searchable=False, args=request.args[:1],
                        links=links, editable=False, deletable=False, details=False)
    posts=db(db.forsale).select(db.forsale.ALL)
    return locals()

#@auth.requires_login()
def voteUp():
    item = db.forsale[request.vars.id]
    new_votes = item.votes + 1
    item.update_record(votes=new_votes)
    return str(new_votes)

@auth.requires_login()
def voteDown():
    item = db.forsale[request.vars.id]
    new_votes = item.votes - 1
    item.update_record(votes=new_votes)
    return str(new_votes)

def view():
    """View a post."""
    p = db.forsale(request.args(0)) or redirect(URL('default', 'index'))
    images=db(db.imageList.forsale_id==p.id).select(db.imageList.ALL)
    image=p.image
    form = SQLFORM(db.forsale, record=p, readonly=True)
    db.imageList.forsale_id.default=p.id
    imgForm = SQLFORM(db.imageList)
    if imgForm.process().accepted:
        # Successful processing.
        session.flash = T("Image added")
        redirect(URL('default', 'view',args=request.args(0)))
    return dict(image=image,form=form, row=p, images=images,imgForm=imgForm)

@auth.requires_login()
def edit():
    """View a post."""
    p = db.forsale(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('Not authorized.')
        redirect(URL('default', 'index'))
    form = SQLFORM(db.forsale, record=p)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'view', args=[p.id]))
    # p.name would contain the name of the poster.
    return dict(form=form)


@auth.requires_login()
@auth.requires_signature()
def toggle_sold():
    #toggle_sold function
    item = db.forsale(request.args(0)) or redirect(URL('default', 'index'))
    item.update_record(sold = not item.sold)
    redirect(URL('default', 'index'))


@auth.requires_login()
@auth.requires_signature()
def delete():
    """Deletes a post.
       Got this code from Luca's homework example
    """
    p = db.forsale(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('Not authorized.')
        redirect(URL('default', 'index'))
    form = FORM.confirm('Are you sure?')
    if form.accepted:
        db(db.forsale.id == p.id).delete()
        redirect(URL('default', 'index'))
    return dict(form=form)


@auth.requires_login()
#@auth.requires_signature()
def add():
    """Add a post."""
    form = SQLFORM(db.forsale)
    if form.process().accepted:
        # Successful processing.
        session.flash = T("inserted")
        redirect(URL('default', 'index'))
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
