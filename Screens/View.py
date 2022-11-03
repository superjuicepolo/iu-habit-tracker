import os
import questionary as quest
from time import sleep
from datetime import datetime
#Function to Clear Terminal
clear = lambda : os.system('tput reset')

import Classes.Analytics as Analytics
from Database import db_api as api
from Load import Habit_Model
from Utils import style

def return_user_screen(state):
    sleep(1*state["SLEEP_SPEED"])
    print('[!] Returning back to User Screen...')
    sleep(1*state["SLEEP_SPEED"])
    clear()
    state["user_screen"](state)

def return_view_screen(state):
    sleep(1*state["SLEEP_SPEED"])
    print('[!] Returning to View Screen...')
    sleep(1*state["SLEEP_SPEED"])
    clear()
    view(state)

def view(state):
    '''The view screen is used to display habits of the user and give various options to see all, an individual or filtered habits. It receives the User-object, active_user, from the user_screen view and also the user_screen function that renders the main menu when exiting the view screen.'''
    clear()
    print('[View Screen]')
    
    #In case the user has no habits or no active habits show message and return.
    if( len(state["active_user"].habits) == 0 or len([habit for habit in state["active_user"].habits if habit.active == True]) < 1): 
        print('You currently do not have any habits to view!')
        return_user_screen(state)

    #If the user has habits, which are not all inactive.
    else:
        options = ['All Habits','Individual Habit', 'Filter Criteria','Go Back to User Screen']
        ans = quest.select('Menu Options:', options).ask()

        def view_all(ans):
            #All Habits
            if(ans == options[0]):
                print(style('[All Active Habits]','UNDERLINE'))
                for habit in state["active_user"].habits:
                    #Only show active habits
                    if habit.active:
                        habit.info_habit()
                        print(style(f'Streak: {habit.streak}','BOLD'))
                        print(style(f'Highest Streak for Habit: {Analytics.habit_longest_streak(habit.checkins)}','BOLD'))
                        print('\n')
                    #Do nothing for inactive habits
                    else:
                        pass
                
                ao2 = ['Global Statistics','[Return]']
                interact = quest.select('See more?',ao2).ask()

                if(interact == ao2[0]):
                    clear()
                    print(style('[Global Statistics for all habits]','UNDERLINE'))
                    print(f'longest_streak: {Analytics.total_longest_streak(state["active_user"].habits)}')
                    print(f'most_punctual_sec:  {Analytics.most_punctual(state["active_user"].habits)}')
                    print(f'most_late_sec: {Analytics.most_late(state["active_user"].habits)}')

                    ao3 = ['Back to All Habits','[Return]']
                    interact2 = quest.select('See more?',ao3).ask()
                    
                    if(interact2==ao3[0]):
                        clear()
                        #all habits
                        view_all(options[0])
                    elif(interact2==ao3[1]):
                        clear()
                        #view screen
                        return_view_screen(state)

                elif(interact == ao2[1]):
                    clear()
                    return_view_screen(state)
            
            #Individual Habit
            elif(ans == options[1]):
                choices = [habit.title for habit in state["active_user"].habits if habit.active] + ['[Return]']
                selected_habit = quest.select('Which habit would you like to individually inspect?', choices).ask()

                for habit in state["active_user"].habits:
                    if habit.title == selected_habit and habit.active:
                        #Now give detailed overview of the habits. Add more individual view options? View Checkins in paginated form?
                        print(f'Viewing habit: {selected_habit}')
                        print(f'Total Successful Checkins: {habit.success}')
                        print(f'Total Failed Checkins: {habit.fail}')
                        print(f'Active Streak: {habit.streak}')
                        print(f'Difficulity: {habit.difficulity}')
                        print(f'Category: {habit.category}')
                        print(f'Importance: {habit.importance}')
                    else: 
                        pass
                
                io2 =  ['Page 2','[Return]']
                interact = quest.select('See more?',io2).ask()
                
                if(interact == io2[0]):
                    print('PAGE 2')
                    print('NOT IMPLEMENTED')
                elif(interact == io2[1]):
                    return_view_screen(state)

                return_view_screen(state)
            
            #Filter Criteria
            elif(ans == options[2]):
                criteria = ['interval','difficulity','category','importance','streak','success','fail','cost','cost_accum']
                ans = quest.select('Which filter criteria would you like to use?',criteria).ask()

                if(ans == 'interval'):
                    interval = quest.text('Write the interval which you would like to use a filter for you habits? E.g. 1D, 4H').ask()
                    
                    if(interval):
                        try:
                            interval_habits = api.db_get_habits_by_attr(state["active_user"].user_id, 'interval', interval)
                            
                            if(len(interval_habits) < 1):
                                print('No habits found for your specified filter criteria.')
                                print('Returning to View screen...')
                                sleep(2)
                                return_view_screen(state)
                            
                            print('\n')
                            for habit in interval_habits:
                                #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                hm = Habit_Model(habit)
                                print(
                                    f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                    f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                    (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                    f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                    f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                    )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get interval: ",e)
                            traceback.print_exc()
                            sleep(10)

                elif(ans == 'difficulity'):
                        difficulity = quest.select('Select the difficulity that you want to use to filter your habits?', ['1','2','3','4','5']).ask()
                        
                        try:
                            if(difficulity):
                                difficulity_habits = api.db_get_habits_by_attr(state["active_user"].user_id, 'difficulity', difficulity)

                                if(len(difficulity_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in difficulity_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)

                elif(ans =='category'):
                        category = quest.text('Provide the category you want to use as a filter, note it is case-sensitive how you defined it! E.g. Sport, Food, Education..?').ask()
                        
                        try:
                            if(category):
                                category_habits = api.db_get_habits_by_attr(state["active_user"].user_id, 'category', category)

                                if(len(category_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in category_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)
                
                elif(ans =='importance'):
                        importance = quest.select('Select the importance that you want to use to filter your habits?', ['1','2','3','4','5']).ask()
                        
                        try:
                            if(importance):
                                importance_habits = api.db_get_habits_by_attr(state["active_user"].user_id, 'importance', importance)

                                if(len(importance_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in importance_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)
                
                elif(ans =='streak'):
                        operator = quest.select('Select one of the operators to use for comparison. Next you will provide a value to compare for. E.g.: streak <= 5, streak > 7', ['>','>=','=','<','<=']).ask()
                        comparison_val = quest.text('Provide a valid number (float or int) that will be used to compare?').ask()
                        try:
                            if(operator and comparison_val):
                                streak_habits = api.db_get_habits_by_attr_operator(state["active_user"].user_id, 'streak', comparison_val, operator)

                                if(len(streak_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in streak_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)
                
                elif(ans =='success'):
                        operator = quest.select('Select one of the operators to use for comparison. Next you will provide a value to compare for. E.g.: success <= 5, success > 7', ['>','>=','=','<','<=']).ask()
                        comparison_val = quest.text('Provide a valid number (float or int) that will be used to compare?').ask()
                        try:
                            if(operator and comparison_val):
                                success_habits = api.db_get_habits_by_attr_operator(state["active_user"].user_id, 'success', comparison_val, operator)

                                if(len(success_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in success_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)
                
                elif(ans =='fail'):
                        operator = quest.select('Select one of the operators to use for comparison. Next you will provide a value to compare for. E.g.: fail <= 5, fail > 7', ['>','>=','=','<','<=']).ask()
                        comparison_val = quest.text('Provide a valid number (float or int) that will be used to compare?').ask()
                        try:
                            if(operator and comparison_val):
                                fail_habits = api.db_get_habits_by_attr_operator(state["active_user"].user_id, 'fail', comparison_val, operator)

                                if(len(fail_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in fail_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)
                
                elif(ans =='cost'):
                        operator = quest.select('Select one of the operators to use for comparison. Next you will provide a value to compare for. E.g.: fail <= 5, fail > 7', ['>','>=','=','<','<=']).ask()
                        comparison_val = quest.text('Provide a valid number (float or int) that will be used to compare?').ask()
                        try:
                            if(operator and comparison_val):
                                cost_habits = api.db_get_habits_by_attr_operator(state["active_user"].user_id, 'cost', comparison_val, operator)

                                if(len(cost_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in cost_habits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)
                    
                elif(ans =='cost_accum'):
                        operator = quest.select('Select one of the operators to use for comparison. Next you will provide a value to compare for. E.g.: cost_accum <= 5, cost_accum > 7', ['>','>=','=','<','<=']).ask()
                        comparison_val = quest.text('Provide a valid number (float or int) that will be used to compare?').ask()
                        try:
                            if(operator and comparison_val):
                                cost_accum_habits = api.db_get_habits_by_attr_operator(state["active_user"].user_id, 'cost_accum', comparison_val, operator)

                                if(len(cost_accum_habits) < 1):
                                    print('No habits found for your specified filter criteria.')
                                    print('Returning to View screen...')
                                    sleep(2)
                                    return_view_screen(state)

                                print('\n')
                                for habit in cost_hcost_accum_habitsabits:
                                        #Converts a unnamed array given by SQLITE of habits to a dict with easy to access attributes
                                        hm = Habit_Model(habit)
                                        print(
                                            f"[{'DYNAMIC' if hm['is_dynamic']==True else 'REGULAR'}] <{hm['interval']}> '{hm['title']}:{hm['description']}' | Moto: {hm['moto']}"+ 
                                            f"\nCategory: {hm['category']} | Difficulity: {hm['difficulity']} | Importance: {hm['importance']} | Milestone Streak: {hm['milestone_streak']}"+
                                            (f"\n{'Required # of Checkins before Deadline:' + str(hm['checkin_num_before_deadline'])} | {'Current # of Checkins before Deadline:' + str(hm['dynamic_count'])}" if hm['is_dynamic']==True else '') +
                                            f"\nStreak: {hm['streak']} | Success:{hm['success']} | Fail: {hm['fail']} | Cost: {hm['cost']}  |  Accumulated Cost: {hm['cost_accum']}"+
                                            f"\nDeadline Due: {hm['next_deadline'].strftime('%Y-%m-%d %H:%M')} |  Created: {hm['created_on'].strftime('%Y-%m-%d %H:%M')}\n"
                                            )

                            print('\n')
                            quest.select('Press Enter to Continue',['Okay']).ask()
                        except Exception as e:
                            print("Failed to get difficulity: ",e)
                            traceback.print_exc()
                            sleep(10)

                return_view_screen(state)
            
            #Return to user screen
            elif(ans == options[3]):
                return_user_screen(state)

        view_all(ans)