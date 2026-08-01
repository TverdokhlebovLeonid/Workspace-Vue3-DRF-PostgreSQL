import type { ScheduleGrid } from '@/types/schedules'
import { makeCellKey } from '@/utils/scheduleCellKey'

export function createScheduleGridFixture(): ScheduleGrid {
  return {
    year: 2026,
    current_start_date: '2026-07-14',
    current_end_date: '2026-07-20',
    start_date: '2026-07-07',
    end_date: '2026-07-20',
    weeks_count: 2,
    days_count: 14,
    weeks: [
      {
        week_index: 1,
        week_start: '2026-07-07',
        is_past: true,
        days: [
          {
            date: '2026-07-10',
            weekday: 4,
            weekday_label: 'Thursday',
            display: '10.07.2026'
          },
          {
            date: '2026-07-14',
            weekday: 1,
            weekday_label: 'Monday',
            display: '14.07.2026'
          },
          {
            date: '2026-07-15',
            weekday: 2,
            weekday_label: 'Tuesday',
            display: '15.07.2026'
          }
        ],
        rows: [
          {
            location: {
              id: 'loc-a',
              name: 'Point A',
              location_type: 'STORE',
              location_type_label: 'Store'
            },
            cells: [
              { date: '2026-07-10', employee_id: 'emp-1', nickname: 'Anna' },
              { date: '2026-07-14', employee_id: 'emp-2', nickname: 'Bob' },
              { date: '2026-07-15', employee_id: null, nickname: '' }
            ]
          }
        ]
      }
    ]
  }
}

export const scheduleGridFixture = createScheduleGridFixture()

export const pastCellKey = makeCellKey('2026-07-10', 'loc-a')
export const currentCellKey = makeCellKey('2026-07-14', 'loc-a')
export const editableCellKey = makeCellKey('2026-07-15', 'loc-a')
