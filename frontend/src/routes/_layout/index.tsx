import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { Dashboard } from "@uppy/react"
import Uppy from "@uppy/core"
import "@uppy/core/dist/style.min.css"
import "@uppy/dashboard/dist/style.min.css"
import XHRUpload from "@uppy/xhr-upload"

import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Upload,
})

function Upload() {
  const { user: currentUser } = useAuth()
  const token = localStorage.getItem("access_token")

  const uppy = new Uppy({
    restrictions: {
      maxFileSize: 5e+10, // 50GB
      maxNumberOfFiles: 5,
      allowedFileTypes: [".parquet", ".csv", ".json", ".xml", ".txt", ".xlsx", ".xls", ".xlsb", ".xlsm", ".avro", ".orc"],
    },
  }).use(XHRUpload, {
    endpoint: `${import.meta.env.VITE_API_URL}/api/v1/uploads`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!currentUser) {
    return null
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Text fontSize="2xl" truncate maxW="m">
        Upload files as {currentUser?.full_name || currentUser?.email}
      </Text>
      <Box bg="white" p={4} borderRadius="md" boxShadow="sm">
        <Dashboard
          uppy={uppy}
          height={400}
          width="100%"
          proudlyDisplayPoweredByUppy={false}
        />
      </Box>
    </Container>
  )
}

export default Upload