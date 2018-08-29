# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from .models import Thumbnail
from django.http import HttpResponse
from io import StringIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from irodsapp import gui_session, irods_interface
from reportlab.lib.units import cm
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from irodsapp.irods_interface import get_collection_name
import io
from reportlab.lib.colors import black
from time import gmtime, strftime
import base64

styles = getSampleStyleSheet()


def get_allowed_ids(session, user, sub_collections, coll_id):
        
    if coll_id == '':
        starting_folder = user.profile.root
    else:
        starting_folder = get_collection_name(coll_id)
    
    filters = gui_session.get_metadata_filters(session)
    
    allowed_ids = gui_session.get_allowed_ids(session)
    
    irods_user_id = irods_interface.get_irods_user_id(user.profile.irods_user)
    thumb_ids = []
    
    if sub_collections:
        if allowed_ids:

            sql = irods_interface.get_thumbnail_list_sql(filters, None)

            for path in allowed_ids.keys():
                coll_id = allowed_ids[path]
                #if path.startswith(starting_folder):
                irods_interface.get_thumbnail_list(sql.format(coll_id, irods_user_id), thumb_ids)
        else:
            sql = irods_interface.get_thumbnail_list_sql(filters, starting_folder)
            formated_sql = sql.format(starting_folder, irods_user_id)
            irods_interface.get_thumbnail_list(formated_sql, thumb_ids)    

    else:
        sql = irods_interface.get_thumbnail_list_sql(filters, None)
        thumb_ids.append(coll_id)
        irods_interface.get_thumbnail_list(sql.format(coll_id, irods_user_id), thumb_ids)

    return thumb_ids
    

def size_label(lbl, nb_of_columns):
    limit = 50
    if nb_of_columns == 2:
        limit = 125

    
    if nb_of_columns == 3:
        limit = 80
        
    if nb_of_columns == 4:
        limit = 60
        
    if nb_of_columns == 5:
        limit = 45
            
    if nb_of_columns == 6:
        limit = 38

    if nb_of_columns == 7:
        limit = 30

    if nb_of_columns == 8:
        limit = 25
                        
    if len(lbl ) > limit:
        return '...' + lbl[-limit:]
    else:
        return lbl
                
@login_required(login_url="/admin/login/")
def create_report(request):
    
    coll_id = request.POST.get('coll_id', None)
    sub_collections = request.POST.get('sub_collections', 'false')    
    sub_collections = sub_collections == 'true'

    nb_of_columns = int(request.POST.get('nb_of_columns', '4'))

    
    session = request.session
    user = request.user
    
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "test.pdf" 
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    
    #buff = StringIO()
    buff = io.BytesIO()
    
    doc = SimpleDocTemplate(buff,pagesize=A4,
                            rightMargin=18,leftMargin=18,
                            topMargin=18,bottomMargin=18)
    
    Story=[]
    
    coll_filters, obj_filters = gui_session.format_filters(session)

    ptext = 'Report created on {}<br/><br/>'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
    if len(coll_filters):
        ptext = ptext + '<b>This report used the following collection filters:</b><br/>'
        for f in coll_filters:
            ptext += f + '<br/>'
        ptext += '<br/>'
    if len(obj_filters):
        ptext = ptext + '<b>This report used the following object filters:</b><br/>'
        for f in obj_filters:
            ptext += f + '<br/>'

    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1,1*cm))

    data = []
    row = []

    thumb_ids = get_allowed_ids(session, user, sub_collections, coll_id)
    print('thumb_ids', thumb_ids)
    thumbs = Thumbnail.objects.filter(id__in=thumb_ids)
    nb_of_thumbs = thumbs.count()
    
    
    print('nb_of_thumbs', nb_of_thumbs)
    
    if nb_of_thumbs > 0:
        if nb_of_thumbs < nb_of_columns:
            nb_of_columns = nb_of_thumbs
        
            # A4 = (21*cm, 29.7*cm)
        width_column = 20 * cm / (nb_of_columns)
        
        print('nb of thumbs:', nb_of_thumbs, nb_of_columns)

        cnt = 0
        col = 0
        for th in thumbs:
            cnt += 1
            if cnt == 2000:
                print('Reached limit')
                break
            image_data = th.image.split("base64,");
            #raw_image_bytes = image_data[1].decode('"base64"')
            raw_image_bytes = base64.b64decode(image_data[1])
            #raw_image_bytes = base64.b64encode(image_data[1]).decode("ascii")
            
            #raw_image_bytes = 'data:image/jpeg;base64,{}'.format(base64.b64encode(file_data.getvalue()).decode("ascii"))
#
            im = Image(io.BytesIO(raw_image_bytes), inch, inch)
            
            scale = im.drawWidth / ( width_column * 0.85)
            im.drawWidth /= scale
            im.drawHeight /= scale
            
            #from os.path import normpath, basename
            #path = basename(normpath( th.folder.name))
            
            header = Paragraph(
                '<para align=center spaceb=3><font size=4>' + size_label(th.folder.name, nb_of_columns) + '</font></para>',
                styles["BodyText"])
            
            footer = Paragraph(
                '<para align=center spaceb=3><font size=4>' + size_label(th.name, nb_of_columns) + '</font></para>',
                styles["BodyText"])
            
            
            row.append( [header,im,footer] )
            col += 1
            if col == nb_of_columns:
                col = 0
                data.append(row)
                row = []
                
        if col != 0:
            data.append(row)
            
    
        t=Table(data,style=[('GRID',(0,0),(-1,-1),0.1,black),
    #          ('BOX',(0,0),(1,-1),2,red),
    #          ('LINEABOVE',(1,2),(-2,2),1,blue),
    #          ('LINEBEFORE',(2,1),(2,-2),1,pink),
    #          ('BACKGROUND', (0, 0), (0, 1), pink),
    #          ('BACKGROUND', (1, 1), (1, 2), lavender),
    #          ('BACKGROUND', (2, 2), (2, 3), orange),
    #          ('BOX',(0,0),(-1,-1),2,black),
    #          ('GRID',(0,0),(-1,-1),0.5,black),
    #          ('VALIGN',(3,0),(3,0),'BOTTOM'),
    #          ('BACKGROUND',(3,0),(3,0),limegreen),
    #          ('BACKGROUND',(3,1),(3,1),khaki),
    #          ('ALIGN',(3,1),(3,1),'CENTER'),
    #          ('BACKGROUND',(3,2),(3,2),beige),
    #          ('ALIGN',(3,2),(3,2),'LEFT'),
         ])
        
        #for i in range(len(t._argW)):
        #    t._argW[i]=width_column
       
        Story.append(t)
    #Story.append(PageBreak())
    #ptext = '<font size=12>Dear Marcel:</font>'
    #Story.append(Paragraph(ptext, styles["Normal"]))
    
    doc.build(Story)

    response.write(buff.getvalue())
    buff.close()
    return response
