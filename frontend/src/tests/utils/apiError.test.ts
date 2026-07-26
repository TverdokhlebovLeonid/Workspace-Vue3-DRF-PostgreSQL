import { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { describe, expect, it } from 'vitest'

import { getApiErrorBody } from '@/utils/apiError'

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
