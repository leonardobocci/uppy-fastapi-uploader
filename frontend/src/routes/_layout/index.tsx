import { Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { Dashboard } from "@uppy/react"
import { useColorModeValue } from "@/components/ui/color-mode"
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
  const allowed_file_types = [".parquet", ".csv", ".json", ".xml", ".txt", ".xlsx", ".xls", ".xlsb", ".xlsm", ".avro", ".orc"]
  const uppyTheme = useColorModeValue("light", "dark")

  const uppy = new Uppy({
    restrictions: {
      maxFileSize: 5e+10, // 50GB
      maxNumberOfFiles: 10,
      allowedFileTypes: allowed_file_types,
    },
    meta: {
      file_datetime: new Date().toISOString(),
    },
  })

  if (!currentUser) {
    return null
  }

  uppy.use(XHRUpload, {
    endpoint: `${import.meta.env.VITE_API_URL}/api/v1/uploads/`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  return (
    <Container maxW="container.xl" py={8}>
      <Text fontSize="2xl" truncate maxW="m">
        Upload files as {currentUser?.full_name || currentUser?.email}
      </Text>
      <Text>
        By default, the file datetime is set to the current date and time in UTC timezone. <br />
        You can change it by clicking the edit button for each file. <br />
        When loading the file, the most recent records will be selected based on this field.
      </Text>
      <Dashboard
        uppy={uppy}
        height={400}
        width="100%"
        proudlyDisplayPoweredByUppy={false}
        theme={uppyTheme === "light" ? "light" : "dark"}
        note={`Up to 50GB, allowed formats: ${allowed_file_types.join(" ")}`}
        metaFields={[
          { id: 'file_datetime', name: 'File Datetime', placeholder: 'This will be used to select the most recent records.' }
        ]}
      />
    </Container>
  )
}

export default Upload
