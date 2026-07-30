import { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { describe, expect, it } from 'vitest'

import { getApiErrorBody, getApiErrorDetail } from '@/utils/apiError'

function axiosErrorWithData(data: unknown): AxiosError {
  return new AxiosError('Request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
    data,
    status: 400,
    statusText: 'Bad Request',
    headers: {},
    config: {} as InternalAxiosRequestConfig
  })
}

describe('getApiErrorBody', () => {
  it('returns undefined for non-axios errors', () => {
    expect(getApiErrorBody(new Error('boom'))).toBeUndefined()
    expect(getApiErrorBody('plain string')).toBeUndefined()
  })

  it('parses string response body', () => {
    expect(getApiErrorBody(axiosErrorWithData('Server error'))).toEqual({
      detail: 'Server error'
    })
  })

  it('parses array response body with string first item', () => {
    expect(getApiErrorBody(axiosErrorWithData(['First error', 'Second error']))).toEqual({
      detail: 'First error'
    })
  })

  it('parses structured object response body', () => {
    const body = {
      code: 'employee_not_assigned_to_location',
      employee_nickname: 'Maria',
      location_name: 'Point A'
    }
    expect(getApiErrorBody(axiosErrorWithData(body))).toEqual(body)
  })
})

describe('getApiErrorDetail', () => {
  it('returns string detail from response body', () => {
    expect(
      getApiErrorDetail(axiosErrorWithData({ detail: 'Employee is not assigned to location.' }))
    ).toBe('Employee is not assigned to location.')
  })

  it('returns first item when detail is an array', () => {
    expect(getApiErrorDetail(axiosErrorWithData({ detail: ['First error', 'Second error'] }))).toBe(
      'First error'
    )
  })

  it('returns undefined when detail is missing', () => {
    expect(
      getApiErrorDetail(axiosErrorWithData({ code: 'employee_not_assigned_to_location' }))
    ).toBeUndefined()
    expect(getApiErrorDetail(new Error('boom'))).toBeUndefined()
  })
})
