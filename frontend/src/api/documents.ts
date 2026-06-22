import { API_DOCUMENTS_PREFIX } from '@/api/constants'
import Http from '@/api/http'
import { unwrapList, type Paginated } from '@/api/utils'
import type { DocumentAccessPayload, DocumentItem } from '@/types/documents'
import type { EntityId } from '@/types/id'

const documentsApi = {
  async getDocuments() {
    const { data } = await Http.get<Paginated<DocumentItem>>(`${API_DOCUMENTS_PREFIX}/`)
    return unwrapList(data)
  },
  async uploadDocument(title: string, file: File) {
    const formData = new FormData()
    formData.append('title', title.trim())
    formData.append('file', file)
    const { data } = await Http.post<DocumentItem>(`${API_DOCUMENTS_PREFIX}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data
  },
  async updateAccess(id: EntityId, payload: DocumentAccessPayload) {
    const { data } = await Http.patch<DocumentItem>(
      `${API_DOCUMENTS_PREFIX}/${id}/access/`,
      payload
    )
    return data
  },
  deleteDocument(id: EntityId) {
    return Http.delete(`${API_DOCUMENTS_PREFIX}/${id}/`)
  },
  async downloadDocument(id: EntityId, fallbackName: string) {
    const response = await Http.get<Blob>(`${API_DOCUMENTS_PREFIX}/${id}/download/`, {
      responseType: 'blob'
    })
    const disposition = response.headers['content-disposition'] as string | undefined
    const match = disposition?.match(/filename="([^"]+)"/)
    const fileName = match?.[1] ?? fallbackName
    const url = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    link.click()
    URL.revokeObjectURL(url)
  }
}

export default documentsApi
