;
; BOSS: This code is written by Elena and modified slightly by dmbiz
; Manga: same but added MaNGA dithering position 
;
pro list_manga,mjd
    compile_opt HIDDEN

    cur_path = '/data/spectro/' + string(mjd, '(I5)') + '/'
    print, 'Reading FITS from ',cur_path

    f1=FINDFILE(cur_path+'sdR*.fit*')
    if STRCOMPRESS(f1[0],/remove) EQ '' then begin
      print, 'No file name'
      goto, m_end
    endif

    f2=file_basename(f1,'*.fit*')  
    f3=strmid(f2,7,8) 
    f1=f1(sort(f3))  & f2=f2(sort(f3)) & f3=f3(sort(f3)) 
     n=N_ELEMENTS(f1)


     if n eq 0 then  begin
        print, 'No file name'
        goto, m_end
     endif

sln=replicate('-',36)
;-d- print,sln
;-d- print,"  n  time filename   crt plt flav Shu Dth  exp  colA   colB   colC   Hrt b1"
;-d- print,sln
kk = 0
prev_name = ''
for i=0,n-1 do begin
  ;-dm-  dat= mrdfits(f1[i], 0, hdr, silent=silent,/UNSIGNED)
   hdr= headfits(f1[i],COMPRESS=1)

   cart_id = FIX( fxpar(hdr,"CARTID") )

   if cart_id GE 1 and cart_id LE 6 then begin
     if i EQ 0 then begin
       print,sln
       print,"  n  time filename   crt plt flav Shu Dth  exp  colA   colB   colC   Hrt b1"
       print,sln
     endif


     seq_name = strmid(f2[i],7,8)
     st_kk = '   '
     if seq_name NE prev_name then begin
      kk = kk + 1
      prev_name = seq_name
      st_kk = STRING(kk, '(i3)')
     endif ;- next sequence

     colla=fxpar(hdr,"COLLA")  & collb=fxpar(hdr,"COLLB")  & collc=fxpar(hdr,"COLLC")
     if finite(colla) then colla=string(colla,format='(i6)') else colla="  NaN"
     if finite(collb) then collb=string(collb,format='(i6)') else collb="  NaN"
     if finite(collc) then collc=string(collc,format='(i6)') else collc="  NaN"

     haha = '    '
     if strmid(fxpar(hdr,"HARTMANN"),0,3) NE 'Out' AND strmid(fxpar(hdr,"FLAVOR"),0,3) EQ 'arc' then haha=' HART'

     manga_dth = STRTRIM( fxpar(hdr,"MGDPOS"), 2)
     if manga_dth EQ '' then manga_dth = ' '

     print, st_kk + ' ' + strmid(fxpar(hdr,"DATE-OBS"),11,5) + ' ' + strmid(f2[i],4,11) + ' ' +$
      string(fxpar(hdr,"CARTID"),'(i2)') + ' ' + string(fxpar(hdr,"PLATEID"),'(i5)') + ' ' + $
      strmid(fxpar(hdr,"FLAVOR"),0,3) + ' ' + strmid(fxpar(hdr,"HARTMANN"),0,3) + ' ' +$
      manga_dth + ' ' + $
      string(fxpar(hdr,"EXPTIME"),'(f6.1)') + ' ' + colla + ' ' + collb + ' ' + collc + ' ' + haha

   endif  ;-- cart_id

endfor 
print,sln

m_end:
print, '--- OK ---'
end
