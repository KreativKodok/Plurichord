#A simple Omnichord lookalike. It uses whatever synth you select in Voices.

"""
by Laszlo Andras Halak / kreativkodok
(2026.05)
"""


import os
import upysh
import tulip
import math
import random

import music
import midi
import synth
import sequencer
import amy

import lvgl as lv

(WIDTH, HEIGHT) = tulip.screen_size()





default_style = lv.style_t()
default_style.set_bg_color(lv.color_white())
default_style.set_border_width(0)
default_style.set_pad_all(0)
default_style.set_radius(0)
default_style.set_pad_row(0)
default_style.set_pad_column(0)



def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        

velocity = 0.6
length = 1000
strum_mode = 0
current_chord_notes = None
midi_out = False
def set_next_chord_cb(chord):
    
    global current_chord_notes
    current_chord_notes = music.Chord(chord).midinotes()


def activate(screen):
    app.synth = midi.config.get_synth(channel=1)
    return
    
def deactivate(screen):
    return

def quit(screen):
    app.synth.all_notes_off()
    for i in range(128):
        app.synth.note_off(i, 0)

    
def set_midi_state(state):
    global midi_out
    midi_out = state
    
current_note = None

def remove_last_note():
    app.synth.note_off(current_note, 0)
    return

def delayed_off(note):
    app.synth.note_off(note, 0)
    global current_note
    #if midi_state:
        #tulip.midi_out([0x80, note, 0])
    if note == current_note:
        current_note = None


def add_note(note):
    global current_note
    if note != current_note:
        current_note = note
        app.synth.note_on(current_note, velocity)
        #tulip.midi_out([0x90, hex(currentNote), hex(math.floor(velocity*0x7f))])
        tulip.defer(delayed_off, note, length)
    
    
    return

old_value = -1
def strum_changed(e):
    global old_value
    global strum_mode
    
    value = math.floor(remap(e.get_target_obj().get_value(), 0, 100, 0, 12))
    if value != old_value:
        
        if strum_mode == 1: # up_down
            index = abs(value-6)+6
        elif strum_mode == 2: # random
            index = random.choice(range(12))
        else:
            index = value
        
        octave = math.floor(index / len(current_chord_notes))
        norm_index = math.floor(index % len(current_chord_notes))
        next_note = current_chord_notes[norm_index]+(octave+1)*12
    	add_note(next_note)
        
    old_value = value
    
    
    
def run(screen):
    
    #syn = synth.PatchSynth(num_voices = 4, patch = 143)
    
    sequencer.tempo(240)

    
    lv.init()
    global app
    global window
    global synth
    
    app = screen
    
    app.synth = midi.config.get_synth(channel=1)
    
    
    app.quit_callback = quit;
    app.activate_callback = activate;
    app.deactivate_callback = deactivate;
    app.handle_keyboard=True
    #set_next_chord_cb("F:min7")
    
    
    app.group.set_style_text_font(lv.font_montserrat_18,0)
    
    window = lv.obj(app.group)
    window.set_size(WIDTH, HEIGHT)
    window.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    window.add_style(default_style, 0)
    window.set_style_bg_color(lv.color_white(),0)
    
    # bar spanning the top of window
    header_bar = lv.obj(window)
    header_bar.set_height(37)
    header_bar.set_width(WIDTH)
    header_bar.add_style(default_style, 0)
    header_bar.set_style_bg_color(lv.palette_main(lv.PALETTE.RED),0)
    title = lv.label(header_bar)
    title.set_pos(20, 10)
    title.set_text('Plurichord v0.1')
   
    #everything goes inside the content_area
    content_area = lv.obj(window);
    content_area.add_style(default_style, 0)
    content_area.set_width(WIDTH)
    content_area.set_style_bg_color(lv.palette_main(lv.PALETTE.TEAL),0)
    content_area.set_flex_grow(1)
    content_area.set_flex_flow(lv.FLEX_FLOW.ROW)
    content_area.update_layout()
    
   # left area for buttons
    chord_choice_area = lv.obj(content_area)
    chord_choice_area.add_style(default_style, 0)
    chord_choice_area.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE),0)
    chord_choice_area.set_height(chord_choice_area.get_parent().get_height())
    chord_choice_area.set_flex_grow(1)
    chord_choice_area.set_flex_flow(lv.FLEX_FLOW.COLUMN)

    # right area for strum
    strum_area = lv.obj(content_area)
    strum_area.add_style(default_style, 0)
    strum_area.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE),0)
    strum_area.set_height(strum_area.get_parent().get_height())
    strum_area.set_width(150)
    
    # update so height can be calculated
    chord_choice_area.update_layout()
    
    strum_container = lv.obj(strum_area)
    strum_container.set_size(strum_container.get_parent().get_width()-50, strum_container.get_parent().get_height()-100)
    strum_container.add_style(default_style, 0)
    strum_container.center()
    
   
    
    # strum slider
    strum_slider = lv.slider(strum_container)
    strum_slider.add_style(default_style, lv.PART.MAIN)
    strum_slider.add_style(default_style, lv.PART.INDICATOR)
    strum_slider.add_style(default_style, lv.PART.KNOB)
    
    strum_slider.set_size(strum_slider.get_parent().get_width(), strum_slider.get_parent().get_parent().get_height()-100)
    
    strum_slider.set_style_bg_color(lv.palette_darken(lv.PALETTE.YELLOW, 2), lv.PART.INDICATOR)
    strum_slider.set_style_bg_color(lv.palette_darken(lv.PALETTE.YELLOW, 2), lv.PART.MAIN)
    strum_slider.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN)
    strum_slider.set_style_bg_color(lv.palette_darken(lv.PALETTE.YELLOW, 2), lv.PART.KNOB)
    strum_slider.center()
    strum_slider.add_event_cb(lambda e: strum_changed(e), lv.EVENT.VALUE_CHANGED, None)
    strum_slider.add_event_cb(lambda e: remove_last_note(), lv.EVENT.RELEASED, None)
    strum_slider.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    strum_slider.set_style_pad_row(5, 0)
    strum_slider.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)
    for b in range(20):
        bar = lv.obj(strum_slider)
        bar.add_style(default_style, 0)
        bar.set_style_bg_color(lv.palette_darken(lv.PALETTE.YELLOW, 4),0)
        bar.set_width(strum_container.get_width()-10)
        bar.set_flex_grow(1)
        bar.remove_flag(lv.obj.FLAG.CLICKABLE)
    
  
    # left area sections
    top_section = lv.obj(chord_choice_area)
    top_section.add_style(default_style, 0)
    top_section.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE,4),0)
    top_section.set_width(top_section.get_parent().get_width())
    top_section.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY)
    top_section.set_flex_grow(4)    
    
    middle_section = lv.obj(chord_choice_area)
    middle_section.add_style(default_style, 0)
    middle_section.set_style_bg_color(lv.color_white(),0)
    middle_section.set_width(middle_section.get_parent().get_width())
    middle_section.set_flex_grow(4)    
    middle_section.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    
    
    bottom_section = lv.obj(chord_choice_area)
    bottom_section.add_style(default_style, 0)
    bottom_section.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE,4),0)
    bottom_section.set_width(bottom_section.get_parent().get_width())
    bottom_section.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY)
    bottom_section.set_flex_grow(1)
    
    
    # chord selection
    title_row = lv.obj(middle_section)
    title_row.add_style(default_style,0)
    title_row.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)
    title_row.set_width(title_row.get_parent().get_parent().get_width())
    title_row.set_flex_grow(1)
    title_row.set_flex_flow(lv.FLEX_FLOW.ROW)
    title_row.set_style_pad_column(10,0)
    title_row.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY)
  
    
    
    major_row = lv.obj(middle_section)
    major_row.add_style(default_style,0)
    major_row.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE,2), 0)
    major_row.set_width(major_row.get_parent().get_parent().get_width())
    major_row.set_flex_grow(1)
    major_row.set_flex_flow(lv.FLEX_FLOW.ROW)
    major_row.set_style_pad_column(10,0)
    major_row.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY)
    major_row.update_layout()
    
    
    minor_row = lv.obj(middle_section)
    minor_row.add_style(default_style,0)
    minor_row.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE,1), 0)
    minor_row.set_width(minor_row.get_parent().get_parent().get_width())
    minor_row.set_flex_grow(1)
    minor_row.set_flex_flow(lv.FLEX_FLOW.ROW)
    minor_row.set_style_pad_column(10,0)
    minor_row.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY)
  
    
    
    seventh_row = lv.obj(middle_section)
    seventh_row.add_style(default_style,0)
    seventh_row.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE,3), 0)
    seventh_row.set_width(seventh_row.get_parent().get_parent().get_width())
    seventh_row.set_flex_grow(1)
    seventh_row.set_flex_flow(lv.FLEX_FLOW.ROW)
    seventh_row.set_style_pad_column(10,0)
    seventh_row.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY,lv.FLEX_ALIGN.SPACE_EVENLY)
  

    
    
    set_next_chord_cb("C:maj")
    chords = ["Db","Ab","Eb","Bb","F","C","G","D","A","E","B","F#"]
    
    def populate(container, chords, mod):
        for key in chords:
            button = lv.button(container)
            button.add_style(default_style,0)
            button.set_style_pad_all(20,0)
            button.set_height(50)
            button.set_flex_grow(2)
            button.set_style_radius(100, lv.PART.MAIN)
            mod_key = key+":"+mod

            button.add_event_cb(lambda e, k = mod_key: set_next_chord_cb(k), lv.EVENT.PRESSED,None)
   

	
    # title row content
    title_row_spacer = lv.obj(title_row)
    title_row_spacer.add_style(default_style,0)
    title_row_spacer.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)
    title_row_spacer.set_flex_grow(4)
    title_row_spacer.set_height(50)
    
    for key in chords:
        label_container = lv.obj(title_row)
        label_container.add_style(default_style,0)
        label_container.set_style_pad_all(20,0)
        label_container.set_height(50)
        label_container.set_flex_grow(2)
        
        col_label = lv.label(label_container)
    	col_label.set_text(key)
    	col_label.set_style_text_color(lv.color_black(),0)
    	col_label.center()
  
	
    title_row_end_spacer = lv.obj(title_row)
    title_row_end_spacer.add_style(default_style,0)
    title_row_end_spacer.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)
    title_row_end_spacer.set_flex_grow(1)
    title_row_end_spacer.set_height(50)
    
    
    # major row content
    major_row_title = lv.obj(major_row)
    major_row_title.add_style(default_style,0)
    major_row_title.set_flex_grow(4)
    major_row_title.set_height(50)
    
    major_label = lv.label(major_row_title)
    major_label.set_text("Major")
    major_label.set_style_text_color(lv.color_black(),0)
    major_label.center()
    
    populate(major_row, chords, "maj")
    
    major_row_spacer = lv.obj(major_row)
    major_row_spacer.add_style(default_style,0)
    major_row_spacer.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE, 2), 0)  
    major_row_spacer.set_flex_grow(1)
    major_row_spacer.set_height(50)
    
    # minor row content
    minor_row_title = lv.obj(minor_row)
    minor_row_title.add_style(default_style,0)
    minor_row_title.set_flex_grow(3)
    minor_row_title.set_height(50)
    
    minor_label = lv.label(minor_row_title)
    minor_label.set_text("Minor")
    minor_label.set_style_text_color(lv.color_black(),0)
    minor_label.center()
    
    populate(minor_row, chords, "min")
    
    minor_row_spacer = lv.obj(minor_row)
    minor_row_spacer.add_style(default_style,0)
    minor_row_spacer.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE, 1), 0)    
    minor_row_spacer.set_flex_grow(2)
    minor_row_spacer.set_height(50)
    
    # seventh row content
    seventh_row_title = lv.obj(seventh_row)
    seventh_row_title.add_style(default_style,0)
    seventh_row_title.set_flex_grow(2)
    seventh_row_title.set_height(50)
    
    seventh_label = lv.label(seventh_row_title)
    seventh_label.set_text("7th")
    seventh_label.set_style_text_color(lv.color_black(),0)
    seventh_label.center()
    
    populate(seventh_row, chords, "min7")
    
    seventh_row_spacer = lv.obj(seventh_row)
    seventh_row_spacer.add_style(default_style,0)
    seventh_row_spacer.set_style_bg_color(lv.palette_lighten(lv.PALETTE.BLUE, 3), 0) 
    seventh_row_spacer.set_flex_grow(3)
    seventh_row_spacer.set_height(50)
    
    
    # top row content
    
    
    # volume knob
    volume_arc = lv.arc(top_section)
    volume_arc.set_size(80,100)
    volume_arc.center()
    volume_arc.set_style_arc_color(lv.color_white(), lv.PART.MAIN)
    volume_arc.set_style_arc_color(lv.palette_main(lv.PALETTE.ORANGE), lv.PART.INDICATOR)
    volume_arc.set_style_bg_color(lv.palette_main(lv.PALETTE.ORANGE), lv.PART.KNOB)
    volume_arc.set_style_pad_hor(0, lv.PART.KNOB)
    volume_arc.set_style_pad_ver(0, lv.PART.KNOB)
    volume_label = lv.label(volume_arc)
    volume_label.set_text("Volume")
    volume_label.set_style_text_color(lv.color_black(), 0)
    volume_label.center()
    volume_label.set_pos(0, 40)
    def adjust_volume_percent(v):
        amy.send(volume = v/10)
        
    volume_arc.add_event_cb(lambda e: adjust_volume_percent(v = e.get_target_obj().get_value()), lv.EVENT.VALUE_CHANGED, None)
    volume_arc.set_value(10)
    adjust_volume_percent(10)
    
    
    # strum mode selector
    
    strum_mode_selector  = lv.roller(top_section)
    strum_mode_selector.set_options("\n".join([
    "Normal",
    "Up-Down",
    "Random"
    ]), lv.roller.MODE.INFINITE)
    strum_mode_selector.set_visible_row_count(2)
    strum_mode_selector.add_style(default_style, lv.PART.MAIN)
    strum_mode_selector.set_style_text_color(lv.color_black(), lv.PART.MAIN)
    strum_mode_selector.add_style(default_style, lv.PART.SELECTED)
    strum_mode_selector.set_style_text_color(lv.color_white(), lv.PART.SELECTED)
    strum_mode_selector.set_style_bg_color(lv.palette_main(lv.PALETTE.ORANGE), lv.PART.SELECTED)
    strum_mode_selector.set_width(120)
    
    def set_strum_mode(mode):
        global strum_mode
        strum_mode = mode
        
        
    strum_mode_selector.add_event_cb(lambda e: set_strum_mode(e.get_target_obj().get_selected()), lv.EVENT.VALUE_CHANGED, None)
    
    
    # velocity knob
    velocity_arc = lv.arc(top_section)
    velocity_arc.set_size(80,100)
    velocity_arc.center()
    velocity_arc.set_style_arc_color(lv.color_white(), lv.PART.MAIN)
    velocity_arc.set_style_arc_color(lv.palette_main(lv.PALETTE.BLUE), lv.PART.INDICATOR)
    velocity_arc.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), lv.PART.KNOB)
    velocity_arc.set_style_pad_hor(0, lv.PART.KNOB)
    velocity_arc.set_style_pad_ver(0, lv.PART.KNOB)
    velocity_arc_label = lv.label(velocity_arc)
    velocity_arc_label.set_text("Velocity")
    velocity_arc_label.set_style_text_color(lv.color_black(), 0)
    velocity_arc_label.center()
    velocity_arc_label.set_pos(0, 40)
    
    def adjust_velocity_percent(v):
        global velocity
        velocity = v/100
        
    velocity_arc.add_event_cb(lambda e: adjust_velocity_percent(v = e.get_target_obj().get_value()), lv.EVENT.VALUE_CHANGED, None)
    velocity_arc.set_value(60)
    adjust_velocity_percent(60)
    
    
    # lenght knob
    length_arc = lv.arc(top_section)
    length_arc.set_size(80,100)
    length_arc.center()
    length_arc.set_style_arc_color(lv.color_white(), lv.PART.MAIN)
    length_arc.set_style_arc_color(lv.palette_main(lv.PALETTE.BLUE), lv.PART.INDICATOR)
    length_arc.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), lv.PART.KNOB)
    length_arc.set_style_pad_hor(0, lv.PART.KNOB)
    length_arc.set_style_pad_ver(0, lv.PART.KNOB)
    length_arc_label = lv.label(length_arc)
    length_arc_label.set_text("Length")
    length_arc_label.set_style_text_color(lv.color_black(), 0)
    length_arc_label.center()
    length_arc_label.set_pos(0, 40)
    
    def adjust_length_percent(v):
        global length
        length = math.floor(remap(v, 0, 100, 100, 3000))
        
    
    length_arc.add_event_cb(lambda e: adjust_length_percent(v = e.get_target_obj().get_value()), lv.EVENT.VALUE_CHANGED, None)
    length_arc.set_value(30)
    adjust_length_percent(30)
    
    """
    
    midi_container = lv.obj(top_section)
    midi_container.add_style(default_style, 0)
    midi_container.set_style_bg_opa(lv.OPA.TRANSP, 0)
    midi_container.set_size(100, 100)
    midi_switch = lv.switch(midi_container)
    midi_switch.center()
    midi_switch.set_pos(0, -10)
    midi_switch.add_event_cb(lambda e: set_midi_state(e.get_target_obj().has_state(lv.STATE.CHECKED)),lv.EVENT.VALUE_CHANGED , None)
    midi_label = lv.label(midi_container)
    midi_label.set_text("MIDI Out")
    midi_label.set_style_text_color(lv.color_black(),0)
    midi_label.center()
    midi_label.set_pos(0, 40)
    """
    
    app.present()
